import pandas as pd
from my_engine import engine, datasea_engine


def get_fund_detail_from_portfolio_changing(portfolio_id):
    amount = {'2021-04-06': {'000011.OF': 5000, '000217.OF': 5000},
              '2021-04-13': {'000217.OF': 1000000},
              '2021-04-15': {'000532.OF': 50},
              '2021-09-14': {'000150.OF': 20000, '000532.OF': 30000, '482002.OF': 50000}}
    return pd.DataFrame(amount).T


def get_portlofio_info(portfolio_id):
    sql = f"""
    SELECT fund_code, fund_chg, trading_day, holding_weight, holding_amount
    FROM portfolio_holding
    WHERE portfolio_id = '{portfolio_id}'
    """
    df = pd.read_sql(sql, engine)
    df.trading_day = df.trading_day.astype(str)
    return df


def get_nav(start_date, fund_code_list):
    fund_code_str = f"{tuple(fund_code_list)}" if len(fund_code_list) > 1 else f"('{fund_code_list[0],}')"
    sql = f"SELECT fund_code, adj_nv_growth_rate as chg, trading_day" \
          f" FROM fund_nv WHERE trading_day >= '{start_date}' AND fund_code IN {fund_code_str}"
    nav = pd.read_sql(sql, datasea_engine)
    nav.trading_day = nav.trading_day.apply(lambda x: x.strftime('%F'))
    nav = nav.pivot(index='trading_day', columns='fund_code', values='chg')
    return nav


def rebuild_df(df, new_column_name):
    df = df.stack()
    df.index = df.index.rename('fund_code', level=1)
    df.name = new_column_name
    df = df.reset_index()
    return df


if __name__ == '__main__':
    # 先从组合info表获取所有存活组合id
    portfolio_id_list = ['a567bee3-ba8d-438e-bd2b-5a397dfbf4df', ]
    for portfolio_id in portfolio_id_list:
        fund_amount = get_fund_detail_from_portfolio_changing(portfolio_id)
        start_date = fund_amount.index[0]
        all_fund_code = fund_amount.columns.to_list()
        nav = get_nav(start_date, all_fund_code)

        create_flag = True
        fund_df = fund_amount.notna().dot(fund_amount.columns + ',').str.rstrip(',')
        ticker_amount_result = []
        ticker_ret_result = []
        ticker_acc_result = []
        ticker_weight_result = []
        for i in range(fund_amount.shape[0] - 1):
            start_date = fund_amount.index[i]
            end_date = fund_amount.index[i + 1]

            # 日收益率
            ret = nav.loc[start_date:end_date]
            if create_flag:
                ret.loc[start_date] = 0  # 建仓日收益为0
                create_flag = False
            else:
                ret = ret.iloc[1:]  # 删除重复的一天
            ticker_ret_result.append(ret)

            # 累计收益率
            acc = ((1 + ret / 100).cumprod() - 1) * 100
            ticker_acc_result.append(acc)

            # 持仓金额
            amount_df = fund_amount.loc[start_date] * (1 + acc / 100)
            amount_df.loc[start_date] = fund_amount.loc[start_date]  # TODO 待定是否需要
            ticker_amount_result.append(amount_df)

            # TODO 持仓占比
            ser = 1 / amount_df.sum(axis=1)
            weight_df = amount_df.mul(ser, axis=0)
            ticker_weight_result.append(weight_df)

        # 处理最后一个
        ret = nav.loc[end_date:].iloc[1:]
        ticker_ret_result.append(ret)

        # 累计收益率
        acc = ((1 + ret / 100).cumprod() - 1) * 100
        ticker_acc_result.append(acc)

        # 持仓金额
        amount_df = fund_amount.loc[end_date] * (1 + acc / 100)
        amount_df.loc[end_date] = fund_amount.loc[end_date]  # TODO 待定是否需要
        ticker_amount_result.append(amount_df)

        # TODO 持仓占比
        ser = 1 / amount_df.sum(axis=1)
        weight_df = amount_df.mul(ser, axis=0)
        ticker_weight_result.append(weight_df)

        # 组合明细持仓, 如果想要用户调仓点的持仓，那么应该设置drop_duplicates(keep='last')
        holding_ret_df = pd.concat(ticker_ret_result)
        holding_acc_df = pd.concat(ticker_acc_result)
        holding_amount_df = pd.concat(ticker_amount_result)
        holding_weight_df = pd.concat(ticker_weight_result)

        ret_df = rebuild_df(holding_ret_df, 'fund_chg')
        acc_df = rebuild_df(holding_acc_df, 'fund_accu_chg')
        amount_df = rebuild_df(holding_amount_df, 'holding_amount')
        weight_df = rebuild_df(holding_weight_df, 'holding_weight')

        a = 1

# 查询调仓表portfolio_changing
