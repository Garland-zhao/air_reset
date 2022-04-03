# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/15 14:31
@Auth ： ZhaoFan
@File ：run.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import pickle
import numpy as np
import pandas as pd
import redis
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler

import settings as ns
from common import load_predata
from common import get_influxdb_client
from common import get_writable_influxdb_client
from common import delete_data_in_ck
from common import write_dataframe_to_ck
from common import get_cache_pool
from common import get_datasea_engine
from common import get_ck_client
from logger import nav_logger as logger


def get_rt_bond_yield(compute_time):
    engine = get_datasea_engine()

    compute_time_str = compute_time.strftime('%F %T')

    # 取得最近数据的时间
    time_query_sql = 'SELECT * FROM bond_yield ORDER BY trade_time DESC limit 1'
    time_query_sql = (
        f'SELECT max(trade_time) FROM bond_yield WHERE bond_code="100101" AND trade_time <= "{compute_time_str}"'
    )
    time_query_res = pd.read_sql(time_query_sql, con=engine)
    latest_time = time_query_res['max(trade_time)'].iloc[-1]

    query_sql = (
        'SELECT trade_time, time_limit, mean_yield FROM bond_yield WHERE bond_code="100101" AND '
        f'trade_time="{latest_time}"'
    )
    rt_bond_yield = pd.read_sql(query_sql, con=engine).pivot(
        index="trade_time", columns="time_limit", values="mean_yield")
    rt_bond_yield.columns = rt_bond_yield.columns.astype(str)
    return rt_bond_yield


def compute_sw_index_return_by_component(df_client, start_time, compute_time, sw_index_component):
    # sw_component_stock_list_str = '|'.join(sw_index_component.columns)
    query_res = df_client.query(
        f"SELECT stock_code, change_rate FROM stock_real_quote WHERE time>='{start_time.isoformat()}' AND "
        f"time<='{compute_time.isoformat()}'"
    )
    sw_component_stock_ret_org = query_res["stock_real_quote"] if "stock_real_quote" in query_res else pd.DataFrame()

    if len(sw_component_stock_ret_org) == 0:
        return pd.DataFrame()

    sw_component_stock_ret_org.stock_code = sw_component_stock_ret_org.stock_code.apply(
        lambda ticker: ticker[:-3] if '.' in ticker else ticker)
    sw_component_stock_ret = sw_component_stock_ret_org.reset_index().pivot(
        index="index", columns="stock_code", values="change_rate").fillna(method="ffill").fillna(0)

    sw_index_ret_df = sw_index_component.dot(sw_component_stock_ret[sw_index_component.columns].T).T
    sw_index_ret = sw_index_ret_df.stack().reset_index().set_index("index")
    sw_index_ret.columns = ["index_code", "change_rate"]
    return sw_index_ret


def get_last_k_ticks(df_client, compute_time, predata, k=2):
    tick_times = df_client.query(
        f"SELECT * FROM index_price WHERE time<='{compute_time.isoformat()}' ORDER BY time DESC limit {k}"
    )
    start_time = tick_times["index_price"].index[0]

    # get realtime index return
    index_list_str = '|'.join(ns.INDEX_LIST)
    query_res = df_client.query(
        f"SELECT * FROM index_price WHERE time>='{start_time.isoformat()}' AND "
        f"time<='{compute_time.isoformat()}' AND index_code=~/{index_list_str}/ tz('Asia/Shanghai')"
    )
    data = query_res["index_price"] if "index_price" in query_res else pd.DataFrame()

    if ns.SW_INDEX_RETURN_BY_COMPONENT:
        sw_data = compute_sw_index_return_by_component(
            df_client, start_time, compute_time, predata['sw_index_component'])
    else:
        # get SYWG index return
        sw_index_list_str = '|'.join(ns.SW_INDEX_CODE)
        sw_query_res = df_client.query(
            f"SELECT * from sw_index_price WHERE time>='{start_time.isoformat()}' AND "
            f"time<='{compute_time.isoformat()}' AND index_code=~/{sw_index_list_str}/ tz('Asia/Shanghai')"
        )
        sw_data = sw_query_res["sw_index_price"] if "sw_index_price" in sw_query_res else pd.DataFrame()

    if len(sw_data) > 0:
        all_index_data = pd.concat([data, sw_data], sort=True)
        last_k_ticks = all_index_data.pivot(columns="index_code", values="change_rate") / 100
        last_k_ticks.index = last_k_ticks.index.tz_convert('Asia/Shanghai')
        return last_k_ticks
    else:
        raise Exception("Failed to get last k ticks.")
    return None


def run_nav_est_steps(df_client, predata, compute_time):
    pca = predata['pca']

    # 读取当前国债收益率
    rt_bond_yield = get_rt_bond_yield(compute_time)

    # 计算国债收益率变化
    preclose_bond_yield = predata['treasury_bond_closing_yield'].sort_index().iloc[-1:]
    bond_yield_mat = pd.concat([preclose_bond_yield, rt_bond_yield[preclose_bond_yield.columns]])
    ytm_mat_diff = bond_yield_mat.astype(np.float32).diff().iloc[-1:] / 100

    # pca.transform 得到 STB 当前因子收益率
    rt_stb_factor_return = pca.transform(ytm_mat_diff)

    # 读取当前指数涨跌幅
    last_k_ticks = get_last_k_ticks(df_client, compute_time, predata, 5).fillna(method="ffill").iloc[-1:]
    rt_all_factor_return = last_k_ticks

    # 合并，得到 行业因子和五因子 涨跌幅
    rt_all_factor_return['shift'] = rt_stb_factor_return[0][0]
    rt_all_factor_return['twist'] = rt_stb_factor_return[0][1]
    rt_all_factor_return['butterfly'] = rt_stb_factor_return[0][2]
    rt_all_factor_return['const'] = 1
    rt_all_factor_return.index = [pd.to_datetime(compute_time).astimezone("Asia/Shanghai")]

    # 第一类
    fund_return_from_industry = predata['fund_industry'].dot(last_k_ticks[ns.SW_INDEX_CODE].T)
    fund_return_from_bond_stb = predata['bond_fund_stb_exposure'].dot(
        rt_all_factor_return[['shift', 'twist', 'butterfly', 'const']].T)
    fund_return_from_bond_stb.columns = ['债券']
    fund_return_from_industry.columns = ['股票']
    fund_return_industry_and_bond = pd.concat(
        [fund_return_from_industry, fund_return_from_bond_stb], axis=1, sort=True).fillna(0)
    fund_return_with_disclosure = (predata['fund_asset_type'] * fund_return_industry_and_bond).sum(axis=1)
    fund_return_with_disclosure.name = pd.to_datetime(compute_time).astimezone("Asia/Shanghai")

    # 第二类：不在第一类里面全部基金
    # 五因子涨跌幅 乘以 各基金在全部因子上的暴露 得到基金涨跌幅
    rest_fund_return = predata['rest_fund_exposure'].dot(
        rt_all_factor_return[predata['rest_fund_exposure'].columns].T)

    # 合并第一类和第二类基金的收益
    fund_return = pd.concat([pd.DataFrame(fund_return_with_disclosure), rest_fund_return], axis=0).T
    return fund_return


def run_nav_est(df_client, cache_pool, input_time=None):
    """运行估值程序"""

    # 计算时间
    if input_time is None:
        input_time = datetime.now(ns.cst_tz)
    compute_time = datetime(input_time.year, input_time.month, input_time.day, input_time.hour, input_time.minute,
                            tzinfo=ns.cst)
    # 预备数据
    predata = load_predata()

    try:
        if compute_time.strftime("%H%M") in ['0929', '0930']:
            # 0929 和 0930 目前没法取到申万行业指数的数据，所以先跳过计算用随机抖动替代
            fund_return = pd.DataFrame(index=[pd.to_datetime(compute_time).astimezone("Asia/Shanghai")],
                                       columns=predata['fund_nav_univ'].columns, data=0)
        else:
            fund_return = run_nav_est_steps(df_client, predata, compute_time)
    except BaseException as err:
        logger.exception(err)
        fund_return = pd.DataFrame(index=[pd.to_datetime(compute_time).astimezone("Asia/Shanghai")],
                                   columns=predata['fund_nav_univ'].columns,
                                   data=[np.random.randint(-20, 20, len(predata['fund_nav_univ'].columns)) / 1e4])

    # 微小扰动
    fund_return = fund_return + pd.DataFrame(index=fund_return.index, columns=fund_return.columns,
                                             data=[np.random.randint(-3, 3, fund_return.shape[1]) / 1e4])
    # 昨日披露净值(单位净值) 乘以 基金涨跌幅 得到 最新基金净值
    latest_nav = predata['fund_unit_nav'].iloc[-1:]
    latest_nav.index = fund_return.index
    latest_fund_nav = latest_nav * (1 + fund_return)

    # 存入 redis
    int_compute_time = int(compute_time.strftime("%Y%m%d%H%M"))

    all_in_one_df = pd.concat([fund_return, latest_fund_nav], axis=1, keys=["r", "nav"])
    all_in_one_df.columns.names = ["key", "ticker"]
    all_in_one_df = all_in_one_df.swaplevel("ticker", "key", axis=1)
    est_nav = all_in_one_df.iloc[-1].round(4).unstack()

    # 设置第二天早上9点过期
    tomorrow = compute_time + timedelta(days=ns.NAVEST_TICKER_BASED_CACHE_EXPIRE)
    tomorrow_expire = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0)

    if compute_time.strftime("%H%M") == "1700":
        # 准备将每天17:00估值结果和真值写入 CK
        navest_ck_df = pd.concat([est_nav['r'], est_nav['nav']], axis=1).reset_index()
        navest_ck_df.columns = ['ticker', 'est_ret', 'est_nav']
        day_str = compute_time.strftime("%Y-%m-%d")
        navest_ck_df['compute_date'] = day_str
        ck_client = get_ck_client()
        # 先删除可能存在的已有数据
        delete_data_in_ck(ck_client, "fund_estimated_nav", f"compute_date='{day_str}'")
        # 写入新算出来的数据
        write_dataframe_to_ck(ck_client, "fund_estimated_nav", navest_ck_df)
        logger.info(f"nav estimation - {int_compute_time} 估值结果写入 CK")

    if cache_pool is not None:
        # 写入 Redis: compute_time -> 全部基金当前时刻的估值 DataFrame
        est_nav_dict = est_nav.to_dict('index')
        est_nav_dict_bytes = pickle.dumps(est_nav_dict)
        cache = redis.Redis(connection_pool=cache_pool)
        cache.set(int_compute_time, est_nav_dict_bytes, ex=ns.NAVEST_CACHE_EXPIRE)

        # 写入influx 时序数据库
        df = est_nav.reset_index()
        # 设置时间
        df["int_compute_time"] = compute_time.strftime("%Y-%m-%dT%H:%M:00Z")
        df["int_compute_time"] = pd.to_datetime(df["int_compute_time"])
        df.set_index("int_compute_time", inplace=True)

        client = get_writable_influxdb_client()
        client.write_points(df, "navest", tag_columns=["ticker"], numeric_precision=8)

        # 写入 Redis: ticker -> list({"r": 0.01, "nav": 1.302, "time": 202201140950})
        with redis.Redis(connection_pool=cache_pool).pipeline() as p:
            for row in est_nav.itertuples():
                # if compute_time.strftime("%H%M") == '0929':
                # p.delete(row[0])
                # p.lpush(row[0], pickle.dumps({"r": row[1], "nav": row[2], "time": int_compute_time}), )
                p.hset(row[0], int_compute_time, pickle.dumps({"r": row[1], "nav": row[2]}))
                # 设置第二天早上9点过期
                p.expireat(row[0], tomorrow_expire)
            p.execute()

        logger.info(f"nav estimation - {int_compute_time} done.")
    else:
        logger.info(f"nav estimation - {int_compute_time} done.")
        return est_nav
    # logger.info(fund_return)
    # logger.info(latest_fund_nav)


if __name__ == "__main__":
    # 构建 influxdb dataframe client 方便操作
    df_client = get_influxdb_client()
    cache_pool = get_cache_pool()

    run_nav_est(df_client, cache_pool)

    date = datetime.today().strftime('%F')

    # TODO 为什么三个任务的开始时间不一样???
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(run_nav_est, trigger='cron', minute='*/1', start_date=f'{date} 09:29:00',
                      end_date=f'{date} 12:00:00', args=[df_client, cache_pool])
    scheduler.add_job(run_nav_est, trigger='cron', minute='*/1', start_date=f'{date} 13:00:00',
                      end_date=f'{date} 16:10:00', args=[df_client, cache_pool])
    scheduler.add_job(run_nav_est, trigger='cron', minute='*/1', start_date=f'{date} 17:00:00',
                      end_date=f'{date} 17:00:00', args=[df_client, cache_pool])

    scheduler.start()
