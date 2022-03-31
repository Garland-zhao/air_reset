import pandas as pd

# pandas.Series( data, index, dtype, name, copy)
# data：一组数据(ndarray 类型)
# index：数据索引标签，如果不指定，默认从 0 开始
# dtype：数据类型，默认会自己判断
# name：设置名称。
# copy：拷贝数据，默认为 False

a = [1, 2, 3]
myvar = pd.Series(a)
print(myvar)
a = ["Google", "Runoob", "Wiki"]  # 非数字类型会显示为dtype: object
myvar = pd.Series(a, index=["x", "y", "z"])
print(myvar)

sites = {1: "Google", 2: "Runoob", 3: "Wiki"}
myvar = pd.Series(sites)  # 字典的key变成了索引值。
print(myvar)

sites = {1: "Google", 2: "Runoob", 3: "Wiki"}
myvar = pd.Series(sites, index=[1, 2])  # 通过指定索引来选择部分字段
print(myvar)  # 只有2个元素

sites = {1: "Google", 2: "Runoob", 3: "Wiki"}
myvar = pd.Series(sites, index=[1, 2], name="RUNOOB-Series-TEST")  # 设置名称
print(myvar)

# pandas.DataFrame( data, index, columns, dtype, copy)
# data：一组数据(ndarray、series, map, lists, dict 等类型)
# index：索引值，或者可以称为行标签, 默认为(0, 1, 2, ..., n)
# columns：列标签，默认为 RangeIndex (0, 1, 2, ..., n)
# dtype：数据类型
# copy：拷贝数据，默认为 False

data = [['Google', 10], ['Runoob', 12], ['Wiki', 13]]
df = pd.DataFrame(data, columns=['Site', 'Age'], dtype=float)
print(df)

data = {'Site': ['Google', 'Runoob', 'Wiki'], 'Age': [10, 12, 13]}
df = pd.DataFrame(data)  # 默认字典的key会作为col, 字典的value作为该列的数据
print(df)

data = [{'a': 1, 'b': 2}, {'a': 5, 'b': 10, 'c': 20}]
df = pd.DataFrame(data)  # 缺少的数值默认用NaN来填充
print(df)

# 使用 loc 属性返回指定行的数据，如果没有设置索引，第一行索引为 0，第二行索引为 1，以此类推：
data = {
    "calories": [420, 380, 390],
    "duration": [50, 40, 45]
}
df = pd.DataFrame(data)
print('默认df')
print(df)
# 返回第一行
print(df.loc[0])
print(type(df.loc[0]))  # 结果是一个Series 数据
# 返回第二行
print(df.loc[1])

# 返回多行数据，使用 [[ ... ]] 格式，... 为各行的索引，以逗号隔开:
data = {
    "calories": [420, 380, 390],
    "duration": [50, 40, 45]
}
# 数据载入到 DataFrame 对象
df = pd.DataFrame(data)
# 返回第一行和第二行
print(df.loc[[0, 1]])
print(type(df.loc[[0, 1]]))  # 结果是一个DataFrame

data = {
    "calories": [420, 380, 390],
    "duration": [50, 40, 45]
}
df = pd.DataFrame(data, index=["day1", "day2", "day3"])  # 指定索引
print(df)
print(df.loc["day2"])

# 只使用部分列时
data = {
    "mango": [420, 380, 390],
    "apple": [50, 40, 45],
    "pear": [1, 2, 3],
    "banana": [23, 45, 56]
}
df = pd.DataFrame(data, index=['a', 'b', 'c'])
print(df)
print(df[["apple", "banana"]])  # 只返回部分指定列时df[['列名1', '列名2'...]]

print('*' * 100)
# -- 处理 CSV
df = pd.read_csv('nba.csv')
print(df)
# to_string() 用于返回 DataFrame 类型的数据，如果不使用该函数，则输出结果为数据的前面 5 行和末尾 5 行，中间部分以 ... 代替。
# print(df.to_string())
# df = df[['Salary']]
# print(df.dtypes)

# 数据处理
print(df.head())  # 默认返回前5行
print(df.head(2))  # 读取前2行
print(df.tail())  # 默认返回最后5行
print(df.tail(2))  # 返回最后2行
print(df.info())  # 返回一些基本信息

# -- 数据清洗
# 判断空值isnull()
print('*' * 100)
df = pd.read_csv('property-data.csv')
print(df['NUM_BEDROOMS'])
print(df['NUM_BEDROOMS'].isnull())

missing_values = ["n/a", "na", "--"]  # Pandas 把 n/a 和 NA 当作空数据，na 不是空数据，不符合我们要求，我们可以指定空数据类型：
df = pd.read_csv('property-data.csv', na_values=missing_values)

print(df['NUM_BEDROOMS'])
print(df['NUM_BEDROOMS'].isnull())

# 清洗空值
# DataFrame.dropna(axis=0, how='any', thresh=None, subset=None, inplace=False)
# axis：默认为 0，表示逢空值剔除整行，如果设置参数 axis＝1 表示逢空值去掉整列
# how：默认为 'any' 如果一行（或一列）里任何一个数据有出现 NA 就去掉整行，如果设置 how='all' 一行（或列）都是 NA 才去掉这整行
# thresh：设置需要多少非空值的数据才可以保留下来的
# subset：设置想要检查的列。如果是多个列，可以使用列名的 list 作为参数
# inplace：如果设置 True，将计算得到的值直接覆盖之前的值并返回 None，修改的是源数据
new_df = df.dropna()
print(new_df.to_string())
df['PID'].fillna(12345, inplace=True)  # 使用 12345 替换 PID列 为空的数据：
