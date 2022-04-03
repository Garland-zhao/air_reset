# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/21 9:15
@Auth ： ZhaoFan
@File ：一些python方法.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
# 返回一段路径的文件名 os.path.basename(path)
import os

path = r'E:\E04_libtorch\TEST_TEMP\x64\Release\config.json'
# print(path.rsplit(r'\', 1)[-1])
print(os.path.basename(path))  # config.json
# 注意:如果path以'／'或'\'结尾，那么就会返回空值
