# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/21 9:05
@Auth ： ZhaoFan
@File ：查看函数参数方法.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import inspect


def foo(bar, baz, spam='eggs', **kw):
    pass


d1 = inspect.getfullargspec(foo)
d2 = inspect.signature(foo)

print(d1)
print(d1.args, type(d1.args))
print(d1.varargs, type(d1.varargs))
print(d1.varkw, type(d1.varkw))
print(d2, type(d2))
print(dir(d2))
print(d2.parameters)

# python 内置方法 func.__code__.co_varnames
d3 = foo.__code__.co_varnames
print(d3, type(d3))
