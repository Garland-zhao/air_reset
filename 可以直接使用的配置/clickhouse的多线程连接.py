# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/31 15:50
@Auth ： ZhaoFan
@File ：clickhouse的多线程连接.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import os
from clickhouse_pool import ChPool

CK_CONFIG = {
    "host": os.getenv("CK_HOST", "172.19.18.137"),
    "port": os.getenv("CK_PORT", 30002),
    "user": os.getenv("CK_USER", "appuser"),
    "password": os.getenv("CK_PASS", "0alVyIO9uTcdYMD"),
    "database": os.getenv("CK_DBNAME", "modelsea"),
    "connections_min": int(os.getenv("CK_CON_MIN", 30)),
    "connections_max": int(os.getenv("CK_CON_MAX", 60)),
    "settings": {'use_client_time_zone': True}
}
# find available settings at https://clickhouse-driver.readthedocs.io/en/latest/api.html#clickhouse_driver.Client
pool = ChPool(**CK_CONFIG)

with pool.get_client() as client:
    # execute sql and print the result
    result = client.execute("SELECT * FROM system.numbers LIMIT 5")
    print(result)

# always close all connections in the pool once you're done with it
pool.cleanup()
