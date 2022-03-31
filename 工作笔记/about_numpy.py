import numpy as np

# np.frombuffer(buffer, dtype=)
s = b'Hello World'
a = np.frombuffer(s, dtype='S1')  # buffer 是字符串的时候，Python3 默认 str 是 Unicode 类型，所以要转成 bytestring 在原 str 前加上 b。
print(a)

# np.fromiter(iterable, dtype, count=-1)
# iterable: 可迭代对象, dtype:返回数组的数据类型, count:读取的数据数量(默认-1表示全部读取)
# 使用 range 函数创建列表对象
list_data = range(5)
it = iter(list_data)
# 使用迭代器创建 ndarray
x = np.fromiter(it, dtype=float)
print(x)

# -- numpy 从数值范围创建数组
# numpy.arange(start, stop, step, dtype)
# 相当于[start, stop) , step: 步长,默认1
a = np.arange(5)
print(a)
b = np.arange(5, 10, 2, dtype=float)
print(b)

# numpy.linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None)
# 用来创建一维数组, 数组是一个等差数列构成的, 差值根据长度和元素数量来决定
# endpoint:该值为 true 时，数列中包含stop值，反之不包含，默认是True。
# num:要生成的等步长的样本数量，默认为50
# retstep: 如果为 True 时，生成的数组中会显示间距，反之不显示。
a = np.linspace(1, 10, 10)
print(a)
a = np.linspace(10, 20, 5, endpoint=False)
print(a)
b = np.linspace(1, 10, 10).reshape([10, 1])
print(b)

# np.logspace(start, stop, num=50, endpoint=True, base=10.0, dtype=None)
# 用来创建一个等比数列
# start	序列的起始值为：base ** start
# stop	序列的终止值为：base ** stop。如果endpoint为true，该值包含于数列中
# num	要生成的等步长的样本数量，默认为50
# endpoint	该值为 true 时，数列中中包含stop值，反之不包含，默认是True。
# base	对数 log 的底数, 默认为10
# dtype	ndarray 的数据类型
a = np.logspace(1.0, 2.0, num=5)  # 以10为底数生成等比数列[10**1, ..., 10**2], 长度为5
print(a)
a = np.logspace(0, 9, num=10, base=2)  # 以2为底数生成等比数列[2**0, ..., 2**9], 长度为10
print(a)

# --numpy的切片和索引, ndarray对象的内容可以通过索引或切片来访问和修改，与 Python 中 list 的切片操作一样。
a = np.arange(10)
print(a)
s = slice(2, 7, 2)  # 从索引 2 开始到索引 7 停止，间隔为2
print(a[s])
b = a[2:7:2]  # 与slice等价
print(b)
print(a[2:])
print(a[2:5])
# 多维数组同样适用
a = np.array([[1, 2, 3], [3, 4, 5], [4, 5, 6]])
print(a)
# 从某个索引处开始切割
print('从数组索引 a[1:] 处开始切割')
print(a[1:])
# 切片还可以包括省略号...来使选择元组的长度与数组的维度相同。
# 如果在行位置使用省略号，它将返回包含行中元素的 ndarray。
a = np.array([[1, 2, 3], [3, 4, 5], [4, 5, 6]])
print('第2列元素')
print(a[..., 1])  # 第2列元素
print('第2行元素')
print(a[1, ...])  # 第2行元素
print('第2列及剩下的所有元素')
print(a[..., 1:])  # 第2列及之后列的所有元素

# -- numpy 高级索引, 除了之前看到的用整数和切片的索引外，数组可以由整数数组索引、布尔索引及花式索引
# 整数数组索引
x = np.array([[1, 2], [3, 4], [5, 6]])
print(x)
y = x[[0, 1, 2], [0, 1, 0]]  # 获取数组中(0,0)，(1,1)和(2,0)位置处的元素。
print('整数数组索引')
print(y)

# TODO 这个没看懂
# 获取了 4X3 数组中的四个角的元素。 行索引是 [0,0] 和 [3,3]，而列索引是 [0,2] 和 [0,2]。
x = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])
print('我们的数组是：')
print(x)
print('\n')
rows = np.array([[0, 0], [3, 3]])
cols = np.array([[0, 2], [0, 2]])
y = x[rows, cols]
print('这个数组的四个角元素是：')
print(y)

# 可以借助切片 : 或 … 与索引数组组合
a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
b = a[1:3, 1:3]
c = a[1:3, [1, 2]]
d = a[..., 1:]
print(b)
print(c)
print(d)

# 布尔索引
x = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]])
print('我们的数组是：')
print(x)
print('\n')
# 现在我们会打印出大于 5 的元素
print('大于 5 的元素是：')
print(x[x > 5])

# 使用了 ~ (取补运算符)来过滤 NaN
a = np.array([np.nan, 1, 2, np.nan, 3, 4, 5])
print('我们的数组是：')
print(a)
print('使用取补运算符排除nan')
print(a[~np.isnan(a)])

a = np.array([1, 2 + 6j, 5, 3.5 + 5j])
print('我们的数组是：')
print(a)
print('过滤掉非复数元素')
print(a[np.iscomplex(a)])

# 花式索引
# TODO https://www.runoob.com/numpy/numpy-advanced-indexing.html 还需要再看
"""
花式索引指的是利用整数数组进行索引。
花式索引根据索引数组的值作为目标数组的某个轴的下标来取值。
对于使用一维整型数组作为索引，如果目标是一维数组，那么索引的结果就是对应下标的行，如果目标是二维数组，那么就是对应位置的元素。
花式索引跟切片不一样，它总是将数据复制到新数组中。
"""
x = np.arange(32).reshape((8, 4))
print('我们的数组是：')
print(a)
print(x[[4, 2, 1, 7]])

# -- numpy 广播 (Broadcast)
"""
广播(Broadcast)是 numpy 对不同形状(shape)的数组进行数值计算的方式， 
对数组的算术运算通常在相应的元素上进行。

如果两个数组 a 和 b 形状相同，即满足 a.shape == b.shape，
那么 a*b 的结果就是 a 与 b 数组对应位相乘。这要求维数相同，且各维度的长度相同。
"""
a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])
print('两个相同shape的数据')
print(a)
print(b)
c = a * b
print('对位相乘')
print(c)
a = np.array([[1, 2], [3, 4]])
b = np.array([[10, 20], [30, 40]])
print('两个相同shape的数据')
print(a)
print(b)
c = a * b
print('对位相乘')
print(c)

# 当运算中的 2 个数组的形状不同时，numpy 将自动触发广播机制。如：
a = np.array([[0, 0, 0],
              [10, 10, 10],
              [20, 20, 20],
              [30, 30, 30]])
b = np.array([1, 2, 3])
print('两个不相同shape的数据')
print(a)
print(b)
print('广播相加')
print(a + b)

a = np.array([[0, 0, 0],
              [10, 10, 10],
              [20, 20, 20],
              [30, 30, 30]])
b = np.array([1, 2, 3])
bb = np.tile(b, (4, 1))  # 重复 b 的各个维度
print('tile后bb')
print(bb)
print(a + bb)
"""
广播的规则:
    让所有输入数组都向其中形状最长的数组看齐，形状中不足的部分都通过在前面加 1 补齐。
    输出数组的形状是输入数组形状的各个维度上的最大值。
    如果输入数组的某个维度和输出数组的对应维度的长度相同或者其长度为 1 时，这个数组能够用来计算，否则出错。
    当输入数组的某个维度的长度为 1 时，沿着此维度运算时都用此维度上的第一组值。
    简单理解：对两个数组，分别比较他们的每一个维度（若其中一个数组没有当前维度则忽略），满足：

数组拥有相同形状。
当前维度的值相等。
当前维度的值有一个是 1。
若条件不满足，抛出 "ValueError: frames are not aligned" 异常。
"""

# -- numpy 迭代数组
# NumPy 迭代器对象 numpy.nditer 提供了一种灵活访问一个或者多个数组元素的方式。
# 迭代器最基本的任务的可以完成对数组元素的访问

a = np.arange(6).reshape(2, 3)
print('原始数组是：')
print(a)
print('\n')
print('迭代输出元素：')
for x in np.nditer(a):
    print(x, end=", ")  # 不换行打印
print('\n')

a = np.arange(0, 60, 5).reshape(3, 4)
print('原始数组是：')
print(a)
print('\n')
print('原始数组的转置是：')
b = a.T  # 行列互换
print(b)
print('\n')
print('以 C 风格顺序排序：')
c = b.copy(order='C')
print(c)
for x in np.nditer(c):
    print(x, end=", ")
print('\n')
print('以 F 风格顺序排序：')
c = b.copy(order='F')
print(c)
for x in np.nditer(c):
    print(x, end=", ")

# 可以通过显式设置，来强制 nditer 对象使用某种顺序：
a = np.arange(0, 60, 5)
a = a.reshape(3, 4)
print('原始数组是：')
print(a)
print('\n')
print('以 C 风格顺序排序：')
for x in np.nditer(a, order='C'):
    print(x, end=", ")
print('\n')
print('以 F 风格顺序排序：')
for x in np.nditer(a, order='F'):
    print(x, end=", ")

# 修改数组中元素的值
a = np.arange(0, 60, 5)
a = a.reshape(3, 4)
print('原始数组是：')
print(a)
print('\n')
for x in np.nditer(a, op_flags=['readwrite']):
    x[...] = 2 * x
print('修改后的数组是：')
print(a)

# --numpy 数组操作
# 修改数组形状
# np.reshape(arr, newshape, order='C')	不改变数据的条件下修改形状
# np.ndarray.flat	    数组元素迭代器
# np.ndarray.flatten	返回一份数组拷贝，对拷贝所做的修改不会影响原始数组
# np.ravel() 展平的数组元素，顺序通常是"C风格"，返回的是数组视图（view，有点类似 C/C++引用reference的意味），修改会影响原始数组。
a = np.arange(8)
print('原始数组：')
print(a)
print('\n')

b = a.reshape(4, 2)
print('修改后的数组：')
print(b)

a = np.arange(9).reshape(3, 3)
print('原始数组：')
for row in a:
    print(row)

# 对数组中每个元素都进行处理，可以使用flat属性，该属性是一个数组元素迭代器：
print('迭代后的数组：')
for element in a.flat:
    print(element)

a = np.arange(8).reshape(2, 4)

print('原数组：')
print(a)
print('\n')
# 默认按行000001, 001385

print('展开的数组：')
print(a.flatten())
print('\n')

print('以 F 风格顺序展开的数组：')
print(a.flatten(order='F'))

a = np.arange(8).reshape(2, 4)

print('原数组：')
print(a)
print('\n')

print('调用 ravel 函数之后：')
print(a.ravel())
print('\n')

print('以 F 风格顺序调用 ravel 函数之后：')
print(a.ravel(order='F'))

# 翻转数组
# numpy.transpose(arr, axes)	对换数组的维度(即转置)
# ndarray.T	和 self.transpose() 相同
# numpy.rollaxis(arr, axis, start)	向后滚动指定的轴  # TODO 没看懂
# swapaxes	对换数组的两个轴

a = np.arange(12).reshape(3, 4)

print('原数组：')
print(a)
print('\n')

print('对换数组：')
print(np.transpose(a))  # 行列互换, 相当于.T
print(a.T)
print('*' * 50)
# 创建了三维的 ndarray
a = np.arange(8).reshape(2, 2, 2)

print('原数组：')
print(a)
print('获取数组中一个值：')
print(np.where(a == 6))
print(a[1, 1, 0])  # 为 6
print('\n')

# 将轴 2 滚动到轴 0（宽度到深度）

print('调用 rollaxis 函数：')
b = np.rollaxis(a, 2, 0)
print(b)
# 查看元素 a[1,1,0]，即 6 的坐标，变成 [0, 1, 1]
# 最后一个 0 移动到最前面
print(np.where(b == 6))
print('\n')

# 将轴 2 滚动到轴 1：（宽度到高度）

print('调用 rollaxis 函数：')
c = np.rollaxis(a, 2, 1)
print(c)
# 查看元素 a[1,1,0]，即 6 的坐标，变成 [1, 0, 1]
# 最后的 0 和 它前面的 1 对换位置
print(np.where(c == 6))
print('\n')

# 创建了三维的 ndarray
a = np.arange(8).reshape(2, 2, 2)

print('原数组：')
print(a)
print('\n')
# 现在交换轴 0（深度方向）到轴 2（宽度方向）TODO 也没看懂

print('调用 swapaxes 函数后的数组：')
print(np.swapaxes(a, 2, 0))

# -- 修改数组维度
# broadcast	产生模仿广播的对象
# broadcast_to	将数组广播到新形状
# expand_dims	扩展数组的形状
# squeeze	从数组的形状中删除一维条目

x = np.array([[1], [2], [3]])
y = np.array([4, 5, 6])

# 对 y 广播 x
b = np.broadcast(x, y)
# 它拥有 iterator 属性，基于自身组件的迭代器元组

print('对 y 广播 x：')
r, c = b.iters

# Python3.x 为 next(context) ，Python2.x 为 context.next()
print(next(r), next(c))
print(next(r), next(c))
print('\n')
# shape 属性返回广播对象的形状

print('广播对象的形状：')
print(b.shape)
print('\n')
# 手动使用 broadcast 将 x 与 y 相加
b = np.broadcast(x, y)
c = np.empty(b.shape)

print('手动使用 broadcast 将 x 与 y 相加：')
print(c.shape)
print('\n')
c.flat = [u + v for (u, v) in b]

print('调用 flat 函数：')
print(c)
print('\n')
# 获得了和 NumPy 内建的广播支持相同的结果

print('x 与 y 的和：')
print(x + y)