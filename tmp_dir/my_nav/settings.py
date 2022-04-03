# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/15 10:33
@Auth ： ZhaoFan
@File ：settings.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import os
from dateutil import tz
from pytz import timezone

cst = tz.gettz("Asia/Shanghai")
cst_tz = timezone("Asia/Shanghai")

PREDATA_PATH = os.getenv('EST_PRE_DATA', "./predata")
try:
    os.mkdir(PREDATA_PATH)
except Exception:
    pass

SASS_URL = 'https://saas.deepredai.com/api/v1/touchstone/overall_estimated_nav_v2'

# navest_predata.py:get_db_engine
JY_DB_CONFIG = {
    "HOST": os.getenv("JY_DB_HOST", "172.19.18.132"),
    "PORT": os.getenv("JY_DB_PORT", 13001),
    "USER": os.getenv("JY_DB_USER", "readuser"),
    "PASS": os.getenv("JY_DB_PASS", "LxkN3Lh1HSLf"),
    "NAME": os.getenv("JY_DB_NAME", "jydb"),
}

INFLUX_DB_CONFIG = {
    "username": os.getenv("INFLUXDB_USER", "readuser"),
    "password": os.getenv("INFLUXDB_PASS", "q6EsWaVTwmkE"),
    "host": os.getenv("INFLUXDB_HOST", "172.19.18.134"),
    "port": os.getenv("INFLUXDB_PORT", 13001),
    "database": os.getenv("INFLUXDB_DB_NAME", "jyrealtime"),
    "pool_size": os.getenv("INFLUXDB_POOL_SIZE", 50),
}

INFLUX_DB_WRITABLE_CONFIG = {
    "username": os.getenv("INFLUXDB_WRITE_USER", "writeuser"),
    "password": os.getenv("INFLUXDB_WRITE_PASS", "xxxx"),
    "host": os.getenv("INFLUXDB_WRITE_HOST", "127.0.0.1"),
    "port": os.getenv("INFLUXDB_WRITE_PORT", 13001),
    "database": os.getenv("INFLUXDB_WRITE_DB_NAME", "testdb"),
    "pool_size": os.getenv("INFLUXDB_POOL_SIZE", 50),
}

# navest_predata.py:get_db_engine
MODEL_DB_CONFIG = {
    "HOST": os.getenv("MODEL_DB_HOST", "172.19.18.134"),
    "PORT": os.getenv("MODEL_DB_PORT", 13003),
    "USER": os.getenv("MODEL_DB_USER", "datauser"),
    "PASS": os.getenv("MODEL_DB_PASS", "uBRDpDKUu4ed"),
    "NAME": os.getenv("MODEL_DB_NAME", "datasea"),
}

MODELSEA_CK_CONFIG = {
    "HOST": os.getenv("MODELSEA_CK_HOST", "172.19.18.137"),
    "PORT": os.getenv("MODELSEA_CK_PORT", 30002),
    "USER": os.getenv("MODELSEA_CK_USER", "appuser"),
    "PASS": os.getenv("MODELSEA_CK_PASS", "0alVyIO9uTcdYMD"),
    "NAME": os.getenv("MODELSEA_CK_NAME", "modelsea"),
}

REDIS_CONFIG = {
    "HOST": os.getenv("REDIS_HOST", "127.0.0.1"),
    "PORT": os.getenv("REDIS_PORT", 6379),
    "PASS": os.getenv("REDIS_PASS", "Eikieng3"),
}

INDEX_LIST = ["399300", "399905"]
# 新申万包好老申万27个行业
SW_INDEX_CODE_27 = ["801010", "801030", "801040", "801050", "801080", "801110",
                    "801120", "801130",
                    "801140", "801150", "801160", "801170", "801180", "801200",
                    "801210", "801230", "801710",
                    "801720", "801730", "801740", "801750", "801760", "801770",
                    "801780", "801790", "801880",
                    "801890"]
# 老申万 28个行业
SW_INDEX_CODE_28 = ["801010", "801020", "801030", "801040", "801050", "801080",
                    "801110", "801120", "801130",
                    "801140", "801150", "801160", "801170", "801180", "801200",
                    "801210", "801230", "801710",
                    "801720", "801730", "801740", "801750", "801760", "801770",
                    "801780", "801790", "801880",
                    "801890"]
# 新申万31个行业
SW_INDEX_CODE_31 = ["801010", "801030", "801040", "801050", "801080", "801110",
                    "801120", "801130", "801140",
                    "801150", "801160", "801170", "801180", "801200", "801210",
                    "801230", "801710", "801720",
                    "801730", "801740", "801750", "801760", "801770", "801780",
                    "801790", "801880", "801890",
                    "801950", "801960", "801970", "801980"]
SW_STANDARD = 24  # 24代表老的28个申万行业，38代表新的31个申万行业，新的31申万行业包含老的27个申万行业
SW_INDEX_CODE = SW_INDEX_CODE_27

SW_INDEX_RETURN_BY_COMPONENT = False

NAVEST_CACHE_EXPIRE = 3600 * 24  # seconds
NAVEST_TICKER_BASED_CACHE_EXPIRE = 30  # days

try:
    from settings_local import *  # noqa
except ImportError:
    pass
