# -*- coding: utf-8 -*-
"""
@Time ： 2022/4/1 18:02
@Auth ： ZhaoFan
@File ：check_diff_pickle.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import pandas as pd

org_df = pd.read_pickle('cluster_20220325.pkl')

for key, val in org_df.items():
    a = key
    b = val

