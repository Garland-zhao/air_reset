import pandas as pd

"""
celery -A my_celery.app worker --loglevel=info
"""
date_list = []
amount_list = []
for i in range(10, 31):
    trading_day = f'2022-03-{i}'
    amount = f'10{i}'
    date_list.append(trading_day)
    amount_list.append(int(amount))
print(len(date_list))
print(len(date_list))
data = {
    'trading_day': date_list,
    'fund_code': ['000001.OF', '000002.OF', '000003.OF'] * 7,
    'amount': amount_list,
}

df = pd.DataFrame(data)
df = df.pivot(index='trading_day', columns='fund_code', values='amount').fillna(0)
print(df)


def get_trading_day_before_a_year(compute_date):
    sql = f"SELECT trading_day FROM trading_day WHERE trading_day >= {compute_date} ORDER BY trading_day LIMIT 1"
    df = pd.read_sql(sql, engine)
    return df.iloc[0][0]


last_day = get_trading_day_before_a_year('2022-03-06')
last


a = 1
"""
app/main/form.py




class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64
    location = StringField('Location', validators=[Length(0, 64)])                                                 )])
 """
