# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/15 10:34
@Auth ： ZhaoFan
@File ：settings_local.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
JY_DB_CONFIG = {
    "HOST": "8.130.182.141",
    "PORT": 13006,
    "USER": "readuser",
    "PASS": "LxkN3Lh1HSLf",
    "NAME": "jydb",
}

INFLUX_DB_CONFIG = {
    "username": "readuser",
    "password": "q6EsWaVTwmkE",
    "host": "172.19.18.134",
    "port": 13001,
    "database": "jyrealtime",
    "pool_size": 50,
}

INFLUX_DB_WRITABLE_CONFIG = {
    "username": "rwuser",
    "password": "6T1SrADThWNDKG",
    "host": "172.19.18.141",
    "port": 10010,
    "database": "jyrealtime",
    "pool_size": 50,
}

MODEL_DB_CONFIG = {
    "HOST": "8.130.12.45",
    "PORT": 13003,
    "USER": "readuser",
    "PASS": "kAldMZgtX3pTcZj",
    "NAME": "datasea",
}

MODELSEA_CK_CONFIG = {
    "HOST": "8.130.17.181",
    "PORT": 30002,
    "USER": "appuser",
    "PASS": "0alVyIO9uTcdYMD",
    "NAME": "modelsea",
}

REDIS_CONFIG = {
    "HOST": "127.0.0.1",
    "PORT": 6379,
    # "PASS": "V9Ncd3AWtnxVI8S",
}
