import pandas as pd
from sqlalchemy import create_engine


pd.set_option('display.max_columns', 1000)
FIRP_MYSQL_CONFIG = {
    'ENGINE': 'mysql',
    'DRIVER': 'pymysql',
    'USER': 'root',
    'PASSWORD': 'devmysql',
    'HOST': '8.130.16.215',
    'PORT': 50001,
    'NAME': 'portfolio',  # 数据库名
}

DATASEA_CONFIG = {
    'ENGINE': 'mysql',
    'DRIVER': 'pymysql',
    'USER': 'readuser',  # 用户名
    'PASSWORD': 'kAldMZgtX3pTcZj',  # 密码
    'HOST': '8.130.12.45',  # 主机
    'PORT': '13003',  # 端口
    'NAME': 'datasea',  # 数据库名
}

uri = '{ENGINE}+{DRIVER}://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}?charset=utf8&autocommit=true'.format(
    **FIRP_MYSQL_CONFIG)
engine = create_engine(uri, pool_size=120, pool_recycle=200, pool_timeout=35, pool_pre_ping=True, max_overflow=50)

datasea_uri = '{ENGINE}+{DRIVER}://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}?charset=utf8&autocommit=true'.format(
    **DATASEA_CONFIG)
datasea_engine = create_engine(datasea_uri, pool_size=120, pool_recycle=200, pool_timeout=35, pool_pre_ping=True,
                               max_overflow=50)