# -*- coding: utf-8 -*-
"""
@Time ： 2022/4/6 14:57
@Auth ： ZhaoFan
@File ：插入数据.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import secrets

from sqlalchemy import create_engine

import uuid

import pandas as pd

pd.set_option('display.max_columns', 1000)
FIRP_MYSQL_CONFIG = {
    'ENGINE': 'mysql',
    'DRIVER': 'pymysql',
    'USER': 'root',
    'PASSWORD': 'devmysql',
    'HOST': '8.130.16.215',
    'PORT': 50001,
    'NAME': 'portfolio',  # 数据库名
}

DATASEA_CONFIG = {
    'ENGINE': 'mysql',
    'DRIVER': 'pymysql',
    'USER': 'readuser',  # 用户名
    'PASSWORD': 'kAldMZgtX3pTcZj',  # 密码
    'HOST': '8.130.12.45',  # 主机
    'PORT': '13003',  # 端口
    'NAME': 'datasea',  # 数据库名
}

uri = '{ENGINE}+{DRIVER}://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}?charset=utf8&autocommit=true'.format(
    **FIRP_MYSQL_CONFIG)
engine = create_engine(uri, pool_size=120, pool_recycle=200, pool_timeout=35, pool_pre_ping=True, max_overflow=50)

datasea_uri = '{ENGINE}+{DRIVER}://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}?charset=utf8&autocommit=true'.format(
    **DATASEA_CONFIG)
datasea_engine = create_engine(datasea_uri, pool_size=120, pool_recycle=200, pool_timeout=35, pool_pre_ping=True,
                               max_overflow=50)


def get():
    pass


def post_detail(sub, manager, trading_day, portfolio_name, fund_info=None):
    portfolio_id = uuid.uuid4()

    df = pd.DataFrame(fund_info)
    df['portfolio_id'] = str(portfolio_id)
    df['portfolio_name'] = portfolio_name
    df['create_date'] = trading_day
    df['sub'] = sub
    df['manager'] = manager

    df.to_sql('portfolio_detail', engine, if_exists='append', index=False)
    return portfolio_id


def compute_portfolio_fund_accu_chg(portfolio_id=None):
    sql = f"""
    SELECT fund_code
    FROM portfolio_holding
    WHERE portfolio_id = '{portfolio_id}' AND FUND
    """
    df = pd.read_sql(sql, engine)
    return df


def post_holding(
        portfolio_id=None,
        trading_day=None,
        fund_info=None,
        rebalance_flag=1,
        _new_portfolio=True
):
    # 基础信息
    df = pd.DataFrame(fund_info)
    df['portfolio_id'] = str(portfolio_id)
    df['holding_weight'] = df.holding_amount / df.holding_amount.sum()
    df['fund_chg'] = 0  # 日收益率统一为0
    df['rebalance_flag'] = rebalance_flag
    df['trading_day'] = trading_day

    # 判断新增组合 or 调仓
    if _new_portfolio:
        df['fund_accu_chg'] = 0  # 累计收益率为0
        df['year_earnings_chg'] = 0  # 年度贡献率为0
    else:
        # 判断该组合是否有过该基金
        compute_portfolio_fund_accu_chg()

    df.to_sql('portfolio_holding', engine, if_exists='append', index=False)
    print('添加完成')


def add_new_data():
    # 新增组合
    # portfolio_id = uuid.uuid4()
    portfolio_id = 'a567bee3-ba8d-438e-bd2b-5a397dfbf4df'
    print('portfolio_id:', str(portfolio_id))
    _today = '2022-03-14'
    funds_info = {
        'fund_code': ['001384.OF', '000828.OF', '001856.OF'],
        'holding_amount': [30000, 30000, 40000],
    }
    post_holding(portfolio_id=portfolio_id, trading_day=_today, fund_info=funds_info)


def daily_insert_holding_table(portfolio_id=None, compute_date=None):
    # 基础参数
    compute_date = '2022-03-15'
    compute_date_yesterday = '2022-03-14'

    # 找到所有的调仓点
    sql = f"""
    SELECT DISTINCT(trading_day)
    FROM portfolio_holding
    WHERE portfolio_id = {portfolio_id} AND rebalance_flag = 1
    ORDER BY trading_day DESC
    """
    trading_day_df = pd.read_sql(sql, engine)
    all_change_day = trading_day_df.trading_day

    # 该组合的基金
    sql = f"""
    SELECT portfolio_id, fund_code, holding_amount as amount
    FROM portfolio_holding
    WHERE portfolio_id = {portfolio_id} 
       AND trading_day = (SELECT MAX(trading_day) FROM portfolio_holding WHERE portfolio_id = {portfolio_id})
    """
    fund_code_df = pd.read_sql(sql, engine)
    fund_code_list = fund_code_df.fund_code.to_list()

    # 日收益率直接直接查询净值表
    fund_code_str = f"{tuple(fund_code_list)}" if len(fund_code_list) > 1 else f"('{fund_code_list[0],}')"
    sql = f"""
    SELECT fund_code, adj_nv_growth_rate as fund_chg, update_time
    FROM fund_nv 
    WHERE fund_code in {fund_code_str} AND update_time >='{compute_date - 1}' AND update_time <= '{compute_date}'
    """
    chg_df = pd.read_sql(sql, datasea_engine)
    df = pd.merge(fund_code_df, chg_df, on='fund_code', how='left')
    df['holding_amount'] = df.amount * (1 + df.fund_chg / 100)
    df['holding_weight'] = df.holding_amount / df.holding_amount.sum()

    # 该组合所有基金的历史记录
    sql = f"""
    SELECT fund_code, fund_chg, trading_day
    FROM portfolio_holding
    WHERE portfolio_id = {portfolio_id} AND trading_day <= {compute_date}
    """
    all_fund_df = pd.read_sql(sql, engine)
    all_fund_df = all_fund_df.pivot(index='trading_day', columns='fund_code', values='fund_chg').sort_index().fillna(0)
    all_fund_df.iloc[0] = 0
    all_fund_df = (1 + all_fund_df / 100).cumprod().tail(1) - 1
    all_fund_df.rename(index={df.index[0]: 'func_acc_chg'}, inplace=True)
    all_fund_df = all_fund_df.T
    df = pd.merge(df, all_fund_df, on='fund_code', how='left')

    # 累计收益率需要查询到该组合下该基金的上次的累计收益率, 若不存在则为0
    sql = f"""
        SELECT fund_code, holding_weight, holding_amount, fund_chg, fund_accu_chg, year_earnings_chg
        FROM portfolio_holding
        
        """
    df = pd.read_sql(sql, engine)

    df['fund_accu_chg'] = ((1 + df.fund_accu_chg) * (1 + df.new_chg / 100) - 1) * 100
    df['year_earnings_chg'] = ((1 + df.year_earnings_chg) * (1 + df.new_chg / 100) - 1) * 100
    df['holding_amount'] = df.holding_amount * (1 + df.new_chg / 100)
    df['holding_weight'] = df['holding_amount'] / df['holding_amount'].sum()
    df = df.drop(columns=['fund_chg', 'update_time'])
    df = df.rename(columns={'new_chg': 'fund_chg'})

    df['portfolio_id'] = "1f4d671b-2c50-41eb-be21-7edf1439e953"
    df['rebalance_flag'] = 1
    df['trading_day'] = compute_date

    # 一年贡献
    sql = f"""
    SELECT fund_chg
    FROM portfolio_holding 
    WHERE portfolio_id = {portfolio_id} AND trading_day BETWEEN {compute_date} AND {compute_date - 252}
    ORDER BY update_time DESC
    """

    df.to_sql('portfolio_holding', engine, if_exists='append', index=False)

    a = 1
    b = 2


if __name__ == '__main__':
    # 添加数据
    # add_new_data()

    # 每日计算持仓表
    daily_insert_holding_table()
