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
