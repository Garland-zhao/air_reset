import numpy as np

data = {i: np.random.randn() for i in range(7)}
print(data)


# 鸭子类型, 检测一个对象是否是可迭代的
def isiterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:  # 不可遍历
        return False


isiterable('string')  # True
isiterable([1, 2, 3])  # True
isiterable(5)  # False


def check_iterable(x):
    if not isinstance(x, list) and isiterable(x):
        x = list(x)


# is, is not 的常用之处就是检查一个变量是否为None
# 因为None只有一个实例
a = None
print(a is None)  # True

tempplate = '{0:.2f} {1:s} are worth US${2:d}'
# {0:.2f}  表示将第一个参数格式化为2位小数的浮点数
# {1:s}  表示将第二个参数格式化为字符串
# {2:d}  表示将第三个参数格式为整数


# 从技术角度来说, None不仅是一个关键字
# 它还是NoneType类型的唯一实例
type(None)  # NoneType

# python 支持链式比较
res = 4 > 3 > 2 > 1
print(res)

# 创建元祖最好的办法, 就是用逗号分割序列值
tup = 1, 2, 3
print(tup)  # (1, 2, 3)

# 元祖和列表都支持通过+号实现拼接
a = [1, 2, 3]
b = [4, 5, 6]
c = a + b
print(c)

# 但是extend是更好的方式, 因为+号操作过程中创建了新列表, 还要复制对象
# everything = []
# for chunk in list_of_lists:
#     everything += chunk
#     everything.extend(chunk)  # extend比+号更快


# python内置函数
"""
enumerate
sorted
zip

"""

# zip的两个使用场景
# 01 与enumerate同时使用
seq1 = ['foo', 'bar', 'baz']
seq2 = ['one', 'two', 'three']
for i, (a, b) in enumerate(zip(seq1, seq2)):
    print(f'{i}, {a}, {b}')
print('*' * 30)

# 02 通过'拆分'序列, 将行的列表转换为列的列表
pitchers = [
    ('Nolan', 'Ryan'),
    ('Roger', '')
]
