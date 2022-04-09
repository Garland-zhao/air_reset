# -*- coding: utf-8 -*-
"""
@Time ： 2022/4/7 17:09
@Auth ： ZhaoFan
@File ：comptue_chg.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import uuid
import pandas as pd
from sqlalchemy import create_engine


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

portfolio_id = 'a567bee3-ba8d-438e-bd2b-5a397dfbf4df'
portfolio_create_date = '2022-03-14'
compute_date = '2022-04-07'

sql = f"""
SELECT fund_code, trading_day, rebalance_flag
FROM portfolio_holding
WHERE portfolio_id = '{portfolio_id}' AND trading_day <= '{compute_date}'
"""
df = pd.read_sql(sql, engine)


# 日收益率直接直接查询净值表
fund_code_list = df.fund_code.to_list()
fund_code_str = f"{tuple(fund_code_list)}" if len(fund_code_list) > 1 else f"('{fund_code_list[0],}')"
chg_sql = f"""
SELECT fund_code, adj_nv_growth_rate as fund_chg, update_time
FROM fund_nv 
WHERE fund_code in {fund_code_str} AND update_time <= '{compute_date}' AND update_time >= '{portfolio_create_date}'
ORDER BY  update_time DESC
"""
chg_df = pd.read_sql(chg_sql, datasea_engine)



a = 1
_df = df.pivot(index='trading_day', columns='fund_code', values='fund_chg').sort_index().fillna(0)
_df.iloc[0] = 0.0
_df = ((1 + _df/100).cumprod() - 1) * 100
df.rename(index={df.index[0]: 'func_acc_chg'}, inplace=True)
df = df.T
a = 1
b = 2

# 年度贡献
# sql = f"""
#     SELECT fund_code, fund_chg, trading_day
#     FROM portfolio_holding
#     WHERE portfolio_id = {portfolio_id} AND trading_day <= {compute_date} AND trading_day >= {last_year}
#     """
# data = {
#     'fund_code': ['001384.OF', '000828.OF', '001384.OF', '000828.OF', '001384.OF', '001856.OF', '001384.OF',
#                   '001856.OF'],
#     'fund_chg': [0.7, 0.6, 0.2, 0.5, 0.3, 0.4, 0.2, 0.1],
#     'trading_day': ['2022-03-04', '2022-03-04', '2022-03-03', '2022-03-03', '2022-03-02', '2022-03-02', '2022-03-01',
#                     '2022-03-01']
# }
# df = pd.DataFrame(data)

