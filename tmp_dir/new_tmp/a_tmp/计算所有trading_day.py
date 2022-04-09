import datetime

import pandas as pd
from my_engine import engine, datasea_engine

pd.set_option('display.max_columns', 1000)
portfolio_create_date = '2022-03-14'
_today = datetime.date.today().strftime('%F')
portfolio_id = 'a567bee3-ba8d-438e-bd2b-5a397dfbf4df'


# 计算所有trading_day
def compute_all_trading_day():
    sql = f"""
    SELECT trading_day FROM trading_days 
    WHERE trading_day < '{_today}' AND trading_day >= '{portfolio_create_date}' 
    ORDER BY trading_day ASC
    """
    all_trading_day_df = pd.read_sql(sql, datasea_engine)
    return all_trading_day_df


def portfolio_all_trading_day():
    sql = f"""
        SELECT DISTINCT(trading_day)
        FROM portfolio_holding
        WHERE portfolio_id = '{portfolio_id}' AND trading_day <= '{_today}'
        """
    df = pd.read_sql(sql, engine)
    return df


def get_all_fund_code_by_portfolio_id():
    sql = f"""
        SELECT fund_code, fund_chg, trading_day, rebalance_flag, holding_weight, holding_amount
        FROM portfolio_holding
        WHERE portfolio_id = '{portfolio_id}'
        """
    df = pd.read_sql(sql, engine)
    df.trading_day = df.trading_day.astype(str)
    return df


def get_all_chg_by_fund_list(fund_code_list):
    fund_code_str = f"{tuple(fund_code_list)}" if len(fund_code_list) > 1 else f"('{fund_code_list[0],}')"
    sql = f"""
        SELECT fund_code, adj_nv_growth_rate as fund_chg, update_time as trading_day
        FROM fund_nv 
        WHERE fund_code in {fund_code_str} AND update_time <= '{_today}' AND update_time > '{portfolio_create_date}'
        ORDER BY  update_time ASC
    """
    df = pd.read_sql(sql, datasea_engine)
    df.trading_day = df.trading_day.apply(lambda x: x.strftime('%F'))
    return df


def rebuild_df(df, new_column_name):
    df = df.stack()
    df.index = df.index.rename('fund_code', level=1)
    df.name = new_column_name
    df = df.reset_index()
    return df


if __name__ == '__main__':
    all_trading_day_df = compute_all_trading_day()
    portfolio_trading_day_df = portfolio_all_trading_day()
    # 检查是否缺少部分交易日的数据
    if all_trading_day_df.shape[0] > portfolio_trading_day_df.shape[0]:
        # 获取缺少的日期
        all_need_trading_day_df = all_trading_day_df[
            ~all_trading_day_df.trading_day.isin(portfolio_trading_day_df.trading_day)]

        fund_info_df = get_all_fund_code_by_portfolio_id()

        chg_df = get_all_chg_by_fund_list(fund_info_df.fund_code.to_list())
        chg_df = chg_df.pivot(index='trading_day', columns='fund_code', values='fund_chg').sort_index().fillna(0)

        fund_code_df = fund_info_df.pivot(index='trading_day', columns='fund_code', values='fund_chg').sort_index()

        fund_amount_df = fund_info_df.pivot(index='trading_day', columns='fund_code', values='holding_amount').sort_index()

        # 日收益率
        df = chg_df
        df.loc[fund_code_df.index] = fund_code_df
        chg = rebuild_df(df, 'fund_chg')
        # 累计收益率
        acc_df = ((1 + df / 100).cumprod() - 1) * 100
        acc = rebuild_df(acc_df, 'fund_acc_chg')

        fund_amount_df = fund_amount_df.iloc[0] * (1+df/100)
        amount = rebuild_df(fund_amount_df, 'holding_amount')
        # 持仓金额


        # 拼接
        add_chg_df = pd.merge(all_need_trading_day_df, chg_df, on='trading_day', how='right')
        add_chg_acc_df = pd.merge(add_chg_df, acc_df, on=['trading_day', 'fund_code'], how='left')
        df = add_chg_acc_df
        df['portfolio_id'] = portfolio_id

        a = 1
    else:
        print('每日更新一条')

    b = 1
