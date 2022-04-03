# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/15 10:31
@Auth ： ZhaoFan
@File ：predata.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import datetime
import numpy as np
import pandas as pd

import statsmodels.api as sm
from sklearn.decomposition import PCA

import settings as ns
from common import DAY
from common import save_predata
from common import get_jy_engine
from common import get_datasea_engine
from logger import nav_logger as logger


def get_jy_trading_days(jy_engine, date_str, limit_days=90):
    """从JY获取距离计算日期最近的X个交易日期"""
    trading_days_sql = f"""
    SELECT TradingDay 
    FROM QT_IndexQuote 
    LEFT JOIN SecuMain ON SecuMain.InnerCode = QT_IndexQuote.InnerCode 
    WHERE SecuCode="399300" 
    AND TradingDay <= '{date_str}'
    ORDER BY TradingDay 
    DESC LIMIT {limit_days}
    """
    trading_days = pd.read_sql(trading_days_sql, con=jy_engine)
    return trading_days


def get_sw_index_component(datasea_engine, date_str):
    """获取距离计算日期最近一天的申万指数成份股权重"""
    latest_date_sql = f"""
    SELECT end_date 
    FROM sw_index_components_weight 
    WHERE end_date <='{date_str}' 
    ORDER BY end_date 
    DESC LIMIT 1
    """
    latest_date_df = pd.read_sql(latest_date_sql, con=datasea_engine)
    latest_date_str = str(latest_date_df.iloc[-1, 0])  # 第-1行, 第0列

    sw_index_list_str = '("' + '","'.join(ns.SW_INDEX_CODE) + '")'
    sw_index_component_sql = f"""
    SELECT index_code, stock_code, weight, end_date 
    FROM sw_index_components_weight 
    WHERE end_date = '{latest_date_str}'
    AND index_code IN {sw_index_list_str}
    """
    latest_sw_index_component_org = pd.read_sql(sw_index_component_sql, con=datasea_engine)

    # df/int 的结果仍为df, 相当于每一个单元格都/100
    latest_sw_index_component = latest_sw_index_component_org.pivot(
        index="index_code", columns="stock_code", values="weight") / 100

    latest_sw_index_component.fillna(0, inplace=True)
    return latest_sw_index_component


def get_mf_industry_allocation(jy_engine, date_str):
    """JY 行业披露"""
    ind_sql = f"""
    SELECT SecuCode, ReportDate, IndustryCode, RatioInNV, UpdateTime 
    FROM MF_FundIndustryAlloY 
    LEFT JOIN SecuMain on SecuMain.InnerCode = MF_FundIndustryAlloY.InnerCode 
    WHERE IndustryStd={ns.SW_STANDARD} 
    AND InvestType=99 
    AND ReportDate >= '2019-12-01'
    AND ReportDate <= '{date_str}'
    """
    fund_industry = pd.read_sql(ind_sql, con=jy_engine)

    sw_list_sql_str = '(\"' + '\",\"'.join(ns.SW_INDEX_CODE) + '\")'
    rel_sql = f"""
    SELECT SecuCode, IndustryCode 
    FROM LC_CorrIndexIndustry 
    LEFT JOIN SecuMain ON SecuMain.InnerCode=LC_CorrIndexIndustry.IndexCode 
    WHERE IndustryStandard={ns.SW_STANDARD} 
    AND SecuCode IN {sw_list_sql_str}
    """
    industry_rel = pd.read_sql(rel_sql, con=jy_engine)

    fund_industry = fund_industry.sort_values(['SecuCode', 'ReportDate', 'IndustryCode'], ascending=False) \
        .drop_duplicates(['SecuCode', 'IndustryCode'])
    fund_industry['IndexCode'] = fund_industry.IndustryCode.replace(
        industry_rel.astype(str).set_index("IndustryCode").to_dict()['SecuCode'])
    return fund_industry.pivot(index="SecuCode", columns="IndexCode", values="RatioInNV").fillna(0)


def get_mf_asset_type_allocation(jy_engine, date_str, limit_days=126):
    """资产类型比例"""
    # 取 limit_days 前的那个交易日，作为数据起点
    trading_days = get_jy_trading_days(jy_engine, date_str, limit_days)
    start_date_str = str(trading_days.iloc[-1, 0])[:10]

    asset_type_allo_sql = f"""
    SELECT SecuCode, ReportDate, AssetType, RatioInNV 
    FROM MF_AssetAllocation
    LEFT JOIN SecuMain ON SecuMain.InnerCode = MF_AssetAllocation.InnerCode 
    WHERE AssetTypeCode IN (10020, 10010) 
    AND ReportDate >= "{start_date_str}" 
    AND ReportDate <= "{date_str}"
    """
    fund_asset_type_allocation_org = pd.read_sql(asset_type_allo_sql, con=jy_engine)

    max_date_df = fund_asset_type_allocation_org.groupby('SecuCode').agg({'ReportDate': max})
    max_date_df = max_date_df.reset_index().set_index(['SecuCode', 'ReportDate'])
    df = fund_asset_type_allocation_org.pivot_table(
        index=['SecuCode', 'ReportDate'], columns='AssetType', values='RatioInNV')
    fund_asset_type_allocation = df.reindex(max_date_df.index).fillna(0)

    return fund_asset_type_allocation


def prepare_for_fund_with_disclosure(jy_engine, date_str):
    """获取基金行业披露、基金资产类型比例、以及此类基金集合"""
    # 行业披露
    fund_industry = get_mf_industry_allocation(jy_engine, date_str)
    # 资产类型比例
    fund_asset_type = get_mf_asset_type_allocation(jy_engine, date_str)

    # 有行业披露，或者有一定债券比例
    fund_with_disclosure = set(fund_asset_type[fund_asset_type['债券'] > 0].unstack().index).union(
        set(fund_industry.index))

    return fund_industry, fund_asset_type, fund_with_disclosure


def get_jy_fund_nav(jy_engine, date_str, limit_days=90, start_date_str=None, tickers=None):
    """从JY获取复权净值表"""
    # 取 limit_days 前的那个交易日，作为数据起点
    if date_str is None:
        trading_days = get_jy_trading_days(jy_engine, date_str, limit_days)
        start_date_str = str(trading_days.iloc[-1, 0])[:10]

    fund_nav_sql = f"""
    SELECT SecuCode, TradingDay, UnitNVRestored, UnitNV 
    FROM MF_FundNetValueRe 
    LEFT JOIN SecuMain ON SecuMain.InnerCode = MF_FundNetValueRe.InnerCode 
    WHERE TradingDay >= '{start_date_str}'
    AND TradingDay < '{date_str}'
    """

    if tickers is not None:
        tickers_str = '("' + '","'.join(tickers) + '")'
        fund_nav_sql += f' AND SecuCode IN {tickers_str}'

    fund_nav_org = pd.read_sql(fund_nav_sql, con=jy_engine)
    fund_nav = fund_nav_org.pivot(index="TradingDay", columns="SecuCode", values="UnitNVRestored")
    fund_unit_nav = fund_nav_org.pivot(index="TradingDay", columns="SecuCode", values="UnitNV")

    return fund_nav, fund_unit_nav


def get_jy_index_return(index_list, jy_engine, date_str, limit_days=90):
    """从JY获取指数因子历史收益率"""
    # 取 limit_days 前的那个交易日，作为数据起点
    trading_days = get_jy_trading_days(jy_engine, date_str, limit_days)
    start_date_str = str(trading_days.iloc[-1, 0])[:10]

    # 取指定 index_list 的日收益率数据
    index_list_str = '("' + "\",\"".join(index_list) + '")'
    index_return_sql = f"""
    SELECT SecuCode, TradingDay, ChangePCT 
    FROM QT_IndexQuote 
    LEFT JOIN SecuMain ON SecuMain.InnerCode = QT_IndexQuote.InnerCode 
    WHERE SecuCode IN {index_list_str} 
    AND TradingDay >= "{start_date_str}"
    AND TradingDay <= "{date_str}"
    """
    index_return_org = pd.read_sql(index_return_sql, con=jy_engine)

    # 取出申万指数
    sw_index_list_str = '("' + '","'.join(ns.SW_INDEX_CODE) + '")'
    sw_index_sql = f"""
    SELECT SecuCode, TradingDay, ChangePCT 
    FROM QT_SYWGIndexQuote 
    LEFT JOIN SecuMain ON SecuMain.InnerCode = QT_SYWGIndexQuote.InnerCode 
    WHERE SecuCode IN {sw_index_list_str} 
    AND TradingDay >= "{start_date_str}" 
    AND TradingDay <= "{date_str}"
    """
    sw_index_org = pd.read_sql(sw_index_sql, con=jy_engine)

    # 这里聚源的数据库很奇怪，QT_IndexQuote 表里面的 ChangePCT 是需要除以100的，而 QT_SYWGIndexQuote 这个表里面
    # 的CHANGEPCT则不需要
    index_return_org['ChangePCT'] = index_return_org['ChangePCT'] / 100
    index_return_org = pd.concat([index_return_org, sw_index_org])
    index_return = index_return_org.pivot(index="TradingDay", columns="SecuCode", values="ChangePCT")

    return index_return


def get_closing_yield(jy_engine, date_str, limit_days=90):
    """从DataSea获取STB因子历史收益率"""
    # bond_code = '100101'
    # 取 limit_days 前的那个交易日，作为数据起点
    trading_days = get_jy_trading_days(jy_engine, date_str, limit_days)
    start_date_str = str(trading_days.iloc[-1, 0])[:10]

    closing_yield_sql = f"""
    SELECT trading_day, pending_period, maturity_yield 
    FROM bond_closing_yield 
    WHERE trading_day>="{start_date_str}" 
    AND trading_day<="{date_str}"
    """
    treasury_ytm = pd.read_sql(closing_yield_sql, con=get_datasea_engine())
    treasury_ytm_df = treasury_ytm.pivot(
        index='trading_day', columns='pending_period', values='maturity_yield').sort_index()
    treasury_ytm_df.index = pd.to_datetime(treasury_ytm_df.index)
    return treasury_ytm_df.reindex(trading_days.iloc[:, 0]).fillna(method="bfill")


def get_jy_live_fund(jy_engine):
    """从JY获取所有存活的基金"""
    live_tickers_sql = f"""
    SELECT SecuCode, MainCode 
    FROM MF_FundArchives 
    LEFT JOIN SecuMain ON SecuMain.InnerCode = MF_FundArchives.InnerCode 
    WHERE ExpireDate is NULL 
    AND FundNature = 1
    """
    live_tickers = pd.read_sql(live_tickers_sql, con=jy_engine)
    return live_tickers


def build_universe(live_tickers_list, fund_nav):
    # 只取目前存续的基金
    universe = set(fund_nav.columns).intersection(set(live_tickers_list))
    # 找到最近10个交易日内没有净值的
    fund_cond = (~fund_nav[universe].iloc[-10:, :].isna()).sum() == 0
    # 减去这些最近没有净值的
    final_universe = universe - set(fund_cond[fund_cond].index)
    return list(final_universe), fund_nav[final_universe]


def compute_exposure(all_factor_return, fund_return):
    all_factor_return['const'] = 1
    exposure = {ticker: sm.OLS(fund_return[ticker], all_factor_return).fit().params
                for ticker in fund_return}
    fund_exposure = pd.DataFrame(exposure).T
    return fund_exposure


def run_predata(jy_engine, limit_days, compute_date_str=None):
    """准备数据

    :param engine: JY数据库连接
    :param limit_days: 截止时间, 默认120天
    :param compute_date_str: 指定的计算日期, str, %Y-%m-%d
    :return:
    """
    if compute_date_str is None:
        compute_date_str = datetime.datetime.now(ns.cst_tz).strftime(DAY)
    logger.info(f">> 开始为 {compute_date_str} 准备数据.")

    # 从DataSea获取申万成份股及权重信息
    sw_index_component = get_sw_index_component(get_datasea_engine(), compute_date_str)
    # 获取基金行业披露、基金资产类型比例、以及此类基金集合
    logger.info(">> 获取基金行业披露、基金资产类型比例、以及此类基金集合...")
    fund_industry, fund_asset_type, fund_with_disclosure = prepare_for_fund_with_disclosure(jy_engine, compute_date_str)
    logger.info(f"完成 - 获取基金行业披露、基金资产类型比例、以及此类基金集合: {len(fund_with_disclosure)}")

    # 获取复权净值表
    logger.info(">> 获取复权净值表...")
    fund_nav, fund_unit_nav = get_jy_fund_nav(jy_engine, compute_date_str, limit_days)
    logger.info(f"完成: {fund_nav.shape}.")

    # 获取指数因子历史收益率
    logger.info(">> 获取指数因子历史收益率...")
    index_return = get_jy_index_return(ns.INDEX_LIST, jy_engine, compute_date_str, limit_days=limit_days)
    logger.info(f"指数因子历史收益率-完成: {index_return.shape}.")

    # 获取STB因子历史收益率
    logger.info(">> 获取STB因子历史收益率...")
    treasury_ytm = get_closing_yield(jy_engine, compute_date_str, limit_days=limit_days)
    treasury_bond_closing_yield = treasury_ytm[[round(float(i), 4) for i in np.arange(0.3, 10.1, 0.1)]]
    treasury_bond_closing_yield.columns = treasury_bond_closing_yield.columns.astype(str)
    treasury_bond_closing_yield = treasury_bond_closing_yield.astype(np.float32).sort_index()
    ytm_mat_diff = treasury_bond_closing_yield.diff().fillna(0) / 100
    pca = PCA(n_components=3)
    factor_return = pca.fit_transform(ytm_mat_diff)
    factor_return = pd.DataFrame(factor_return, index=ytm_mat_diff.index)
    factor_return.columns = ["shift", "twist", "butterfly"]
    logger.info(f"完成 - STB因子历史收益率: {factor_return.shape}.")

    # 对齐时间
    logger.info(">> 对齐时间...")
    valid_index = index_return.index
    factor_return = factor_return.reindex(valid_index).fillna(0)
    fund_nav = fund_nav.reindex(valid_index)
    fund_unit_nav = fund_unit_nav.reindex(valid_index)
    logger.info(f"完成: {index_return.shape, factor_return.shape, fund_nav.shape}.")

    # 构建基金池 - 总池子（当前存活的、近期有净值的基金）
    logger.info(">> 构建基金池...")
    live_tickers = get_jy_live_fund(jy_engine)
    live_tickers_list = live_tickers['SecuCode'].tolist()
    universe, fund_nav_univ = build_universe(live_tickers_list, fund_nav)
    fund_nav_univ = fund_nav_univ.fillna(method="ffill").fillna(method="bfill")
    fund_return = fund_nav_univ.pct_change().fillna(0)
    # 处理单位净值，并对其 columns
    fund_unit_nav = fund_unit_nav.fillna(method="ffill").fillna(method="bfill")
    fund_unit_nav = fund_unit_nav[fund_return.columns]
    logger.info(f"完成 - fund_return shape: {fund_return.shape}...")

    # 含债类的基金在STB上的暴露
    logger.info(">> 计算含债类的基金在STB上的暴露...")
    bond_fund_df = fund_asset_type[fund_asset_type['债券'] > 0]
    bond_fund = set(bond_fund_df.unstack().index).intersection(set(fund_return.columns))
    bond_fund_stb_exposure = compute_exposure(factor_return, fund_return[bond_fund])
    logger.info(">> 完成 - 计算含债类的基金在STB上的暴露...")

    # 分类：
    # universe = live_fund_with_disclosure + rest_fund
    # live_fund_with_disclosure = live_fund_with_industry.union(live_bond_fund)

    # 第一类：存活的、有行业披露的基金
    live_fund_with_disclosure = set(fund_with_disclosure).intersection(set(universe))
    # 第一类中有行业披露的基金：完全被第一类基金所包含
    live_fund_with_industry = set(fund_industry.index).intersection(set(live_fund_with_disclosure))
    # 第一类中的含债基金：完全被第一类基金所包含
    live_bond_fund = bond_fund.intersection(set(live_fund_with_disclosure))
    # 第二类：不在第一类里面全部基金
    rest_fund = set(universe) - live_fund_with_disclosure

    fund_industry = fund_industry.loc[live_fund_with_industry]
    bond_fund_stb_exposure = bond_fund_stb_exposure.loc[live_bond_fund]
    fund_asset_type = fund_asset_type.droplevel(1)
    same_index = fund_asset_type.index.intersection(live_fund_with_disclosure)
    fund_asset_type = fund_asset_type.loc[sorted(same_index)]

    # 构建五因子历史收益率
    logger.info(">> 构建五因子历史收益率...")
    five_factor_return = pd.concat([index_return[ns.INDEX_LIST], factor_return], axis=1)
    logger.info(f"完成 - five_factor_return shape: {five_factor_return.shape}...")

    # 计算第二类基金在五因子上的暴露
    logger.info(">> 计算第二类基金在五因子上的暴露...")
    rest_fund_exposure = compute_exposure(five_factor_return, fund_return[rest_fund])
    logger.info(f"完成 - rest_fund_exposure shape: {rest_fund_exposure.shape}.")

    predata = {
        "universe": universe,
        "live_fund_with_disclosure": live_fund_with_disclosure,
        "live_fund_with_industry": live_fund_with_industry,
        "live_bond_fund": live_bond_fund,
        "rest_fund": rest_fund,
        "fund_asset_type": fund_asset_type,
        "index_return": index_return,
        "sw_index_component": sw_index_component,
        # 用于计算有行业披露的基金的估值
        "fund_industry": fund_industry[ns.SW_INDEX_CODE],
        # 用于计算含债类的基金的债这一部分的估值
        "bond_fund_stb_exposure": bond_fund_stb_exposure,
        # 用于计算第二类基金的实时估值（通过五因子方法）
        "rest_fund_exposure": rest_fund_exposure,
        # 用于计算基金实时净值
        "fund_nav_univ": fund_nav_univ,
        # 以下两项用于计算STB因子的实时收益率
        "treasury_bond_closing_yield": treasury_bond_closing_yield,
        # 用于输出估值, 收益率需要乘以单位净值才行
        "fund_unit_nav": fund_unit_nav,
        "pca": pca
    }
    logger.info(f">> 数据准备完成 - {compute_date_str}")
    return predata


if __name__ == '__main__':
    # 准备数据
    predata = run_predata(get_jy_engine(), 120)

    # 数据数据写入到.dat文件中
    logger.info(">> 将predata写入文件...")
    save_predata(predata)
    logger.info("完成.")
