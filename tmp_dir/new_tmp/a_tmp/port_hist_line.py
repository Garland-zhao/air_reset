#!/usr/bin/env python
# coding=utf-8
def port_hist_line(nav, weight):
    ''' 计算历史收益曲线, 每个点相对于其调仓点的历史收益
        原理如下:
            假设起始买入金额为 a，b
            期间收益：a的日收益率为 x1,x2. b 的日收益为 y1,y2
            期间收益（相对与调仓点）:  a:(1+x1)(1+x2)-1. b: (1+y1)(1+y2)
            那么到期金额为 a*(1+x1)(1+x2) + b * (1+y1)(1+y2)
            到期收益为  a*(1+x1)(1+x2) + b * (1+y1)(1+y2) - (a+b) 
            提取公因式得到 a*((1+x1)(1+x2) - 1) + b((1+y1)(1+y2)-1)
            到期收益率为：(（a*((1+x1)(1+x2) - 1) + b((1+y1)(1+y2)-1)  ) / (a+b)
            另：Wa = a/(a+b), Wb=b/(a+b) 即初始权重
            那么到期收益率降得到：Wa*X + Wb * Y, 其中 X 为 这 a标的在两期的总收益 收益向量，同理 Y
            那么得到公式： r = W*R, 其中 W 为 标的初始权重向量，R 为期间总收益向量
            如果nav 代表某段期间净值
            那么 ret = nav.pct_change(), 其中 ret 为每期的收益
            这段时间各个点的期间收益为 R = (1+ret).cumprod() - 1
            那么期间总收益为 W*R， 其中 W 为各标的的初始权重

        参数示例：
        nav: 理论上说需要时间范围应该是 从第一个调仓点开始，结束日期应超过最后一个调仓点
                    000011.OF  000217.OF  482002.OF  000150.OF  000532.OF
        DATE
        2018-04-04    23.0515     0.9997   1.484520     1.4588      1.812
        2018-04-09    22.9371     0.9974   1.485351     1.4601      1.810
        2018-04-10    23.3470     0.9991   1.485527     1.4614      1.836
        2018-04-11    23.3963     1.0024   1.485689     1.4614      1.846
        2018-04-12    23.2890     1.0068   1.485851     1.4614      1.844
        ...               ...        ...        ...        ...        ...
        2019-09-06    25.1898     1.2725   1.553034     1.5581      2.190
        2019-09-09    25.2904     1.2700   1.553327     1.5596      2.194
        2019-09-10    25.1395     1.2525   1.553427     1.5593      2.193
        2019-09-11    25.0370     1.2550   1.553526     1.5586      2.162
        2019-09-12    25.2196     1.2572   1.553624     1.5582      2.180

        weight:
            {'2018-04-04': {'000011.OF': 0.166538, '000217.OF': 0.298218},
            '2018-09-14': {'000150.OF': 0.240703,
                            '000532.OF': 0.18033,
                            '482002.OF': 0.578967}}
        weight_df (如果是 dataframe 类型):
                    000011.OF  000217.OF  482002.OF  000150.OF  000532.OF
        2018-04-04   0.166538   0.298218        NaN        NaN        NaN
        2018-09-14        NaN        NaN   0.578967   0.240703    0.18033
    '''
    if isinstance(weight, dict):
        weight_df = pd.DataFrame(weight).T
    if isinstance(weight, DataFrame):
        weight_df = weight

    port_ret = []
    last_ret = 0
    for i in range(len(weight_df) - 1):
        start_date = weight_df.index[i]
        end_date = weight_df.index[i + 1]
        df = nav.loc[start_date:end_date]
        # 累积收益率，相对于调仓点
        sub_ret = (df.pct_change() + 1).cumprod() - 1
        sub_weight = weight_df.iloc[i]

        sub_port_ret = (sub_ret * sub_weight).sum(axis=1)
        # 分段计算，需要把两段之间连接起来
        sub_port_ret = (last_ret + 1) * (sub_port_ret + 1) - 1
        # 如果是第一个调仓点， 那么不需要截取第一天
        if port_ret:
            sub_port_ret = sub_port_ret.iloc[1:]
        port_ret.append(sub_port_ret)
        last_ret = sub_port_ret.iloc[-1]

    # 处理最后一个调仓点
    end_date = weight_df.index[-1]
    df = nav.loc[end_date:]
    sub_ret = (df.pct_change() + 1).cumprod() - 1
    sub_weight = weight_df.loc[end_date]
    sub_port_ret = (sub_ret * sub_weight).sum(axis=1)
    # 如果是第一个调仓点， 那么不需要截取第一天
    if port_ret:
        sub_port_ret = sub_port_ret.iloc[1:]
    sub_port_ret = (last_ret + 1) * (sub_port_ret + 1) - 1
    port_ret.append(sub_port_ret)

    hist_line = pd.concat(port_ret)

    print(hist_line)
    return hist_line


def hist_line_amount(nav, amount):
    if isinstance(amount, dict):
        amount = pd.DataFrame(amount).T
    """
    amount_df
                    000011.OF  000217.OF   000532.OF  000150.OF  482002.OF
    2021-04-06       5000.0     5000.0        NaN        NaN        NaN
    2021-04-10        NaN      1000000.0      NaN        NaN        NaN
    2021-04-11        NaN        NaN         50.0        NaN        NaN
    2021-09-14        NaN        NaN        30000.0    20000.0    50000.0
    """
    # 标的每日持仓
    ticker_amount_result = []
    # 入参与第一种方式格式一样，只不过 weight 变成了 amount
    for i in range(amount.shape[0] - 1):
        start_date = amount.index[i]
        end_date = amount.index[i + 1]
        df = nav.loc[start_date:end_date]
        ret = (df.pct_change() + 1).cumprod()
        amount_df = amount.loc[start_date] * ret
        # 将调仓点的持仓加进去
        amount_df.loc[start_date] = amount.loc[start_date]
        ticker_amount_result.append(amount_df)

    # 处理最后一个
    df = nav.loc[end_date:]
    ret = (df.pct_change() + 1).cumprod()
    amount_df = amount.loc[end_date] * ret
    amount_df.loc[end_date] = amount.loc[end_date]
    ticker_amount_result.append(amount_df)

    # 组合明细持仓, 如果想要用户调仓点的持仓，那么应该设置drop_duplicates(keep='last')
    port_detail_amount_df = pd.concat(ticker_amount_result)
    # 组合每日总持仓, 如果想要用户调仓点的持仓，那么应该设置 keep='last'
    port_amount_df = port_detail_amount_df.sum(axis=1)

    # 组合日收益率,真实收益率需要 keep = 'first'
    # 因为把调仓点的持仓加进去了，上一个调仓点在计算持仓时，把下一个调仓点的持仓计算出来
    # 这里需要剔除 这两个相同调仓点的收益率，剔除的是第二个，因为是按顺序 concat 的

    # 每日收益
    port_daily_increase = port_amount_df.diff()
    port_daily_increase = port_daily_increase[~port_daily_increase.index.duplicated(keep='first')]
    # 每日收益率
    port_daily_ret = port_amount_df.pct_change().fillna(0)
    port_daily_ret = port_daily_ret[~port_daily_ret.index.duplicated(keep='first')]

    # 处理每日组合明细及每日组合总持仓
    # 调仓点的数据是计算出来的数据
    port_detail_amount_df1 = port_detail_amount_df[~port_detail_amount_df.index.duplicated(keep='first')]
    port_amount_df1 = port_amount_df[~port_amount_df.index.duplicated(keep='first')]
    # 调仓点的数据是用户输入的数据
    port_detail_amount_df2 = port_detail_amount_df[~port_detail_amount_df.index.duplicated(keep='last')]
    port_amount_df2 = port_amount_df[~port_amount_df.index.duplicated(keep='last')]
    return port_daily_ret


import pandas as pd
from my_engine import engine, datasea_engine

start_date = '2021-04-06'
weight = {'2021-04-06': {'000011.OF': 0.5, '000217.OF': 0.5},
          '2021-04-13': {'000217.OF': 1},
          '2021-04-15': {'000532.OF': 1},
          '2021-09-14': {'000150.OF': 0.2, '000532.OF': 0.3, '482002.OF': 0.5}}

amount = {'2021-04-06': {'000011.OF': 5000, '000217.OF': 5000},
          '2021-04-13': {'000217.OF': 1000000},
          '2021-04-15': {'000532.OF': 50},
          '2021-09-14': {'000150.OF': 20000, '000532.OF': 30000, '482002.OF': 50000}}
# nav = pd.read_csv('sub_nav.csv', index_col=0)
    # nav = nav.loc[start_date:]
sql = f"SELECT fund_code, adj_nv, trading_day" \
      f" FROM fund_nv WHERE trading_day >= '{start_date}' AND fund_code IN ('000011.OF','000217.OF', '000532.OF', " \
      f"'000150.OF', '482002.OF') "
nav = pd.read_sql(sql, datasea_engine)
nav.trading_day = nav.trading_day.apply(lambda x: x.strftime('%F'))
nav = nav.pivot(index='trading_day', columns='fund_code', values='adj_nv')
a = 1
daily_ret = hist_line_amount(nav, amount)
hist_ret1 = (1 + daily_ret).cumprod() - 1
hist_ret2 = port_hist_line(nav, weight)
