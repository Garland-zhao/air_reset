# python 的小数据池, None和一个空字符串''是等价的
a = 'abc 1234'
data = a.split(None)
for i in data:
    print(i)
print("***********************")
data = a.split(' ')
for i in data:
    print(i)
print("#######################")

a = 'abc  1234'
data = a.split(None)
for i in data:
    print(i)
print("***********************")
data = a.split(' ')
for i in data:
    print(i)
