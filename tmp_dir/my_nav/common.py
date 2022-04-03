# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/15 10:36
@Auth ： ZhaoFan
@File ：common.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import os
import glob
import pickle
import datetime

import redis
import pandas as pd
from influxdb import DataFrameClient
from sqlalchemy import create_engine
from clickhouse_driver import Client as CKClient

import settings as ns
from logger import nav_logger as logger

# MySQL数据库连接uri
SQL_URI = 'mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8'

# date格式化
DAY = '%Y-%m-%d'


def save_predata(predata):
    """将predata写入到文件中"""
    time_suffix = datetime.datetime.now().strftime('%Y%m%d%H%M')
    filename = os.path.join(ns.PREDATA_PATH, f"predata_{time_suffix}.dat")
    with open(filename, "wb") as f:
        pickle.dump(predata, f, protocol=4)


def get_jy_engine():
    """JY-MySQL连接"""
    jy_conn = SQL_URI.format(
        user=ns.JY_DB_CONFIG["USER"],
        pwd=ns.JY_DB_CONFIG["PASS"],
        host=ns.JY_DB_CONFIG["HOST"],
        port=ns.JY_DB_CONFIG["PORT"],
        db=ns.JY_DB_CONFIG['NAME']
    )
    return create_engine(jy_conn, echo=False)


def get_datasea_engine():
    """DataSea-MySQL连接"""
    datasea_conn = SQL_URI.format(
        user=ns.MODEL_DB_CONFIG["USER"],
        pwd=ns.MODEL_DB_CONFIG["PASS"],
        host=ns.MODEL_DB_CONFIG["HOST"],
        port=ns.MODEL_DB_CONFIG["PORT"],
        db=ns.MODEL_DB_CONFIG['NAME']
    )
    return create_engine(datasea_conn, echo=False)


def get_influxdb_client():
    """只读InfluxDB连接"""
    return DataFrameClient(**ns.INFLUX_DB_CONFIG)


def get_writable_influxdb_client():
    """可写InfluxDB连接"""
    return DataFrameClient(**ns.INFLUX_DB_WRITABLE_CONFIG)


def get_ck_client():
    """ClickHouse连接"""
    ck_client = CKClient(host=ns.MODELSEA_CK_CONFIG["HOST"],
                         port=ns.MODELSEA_CK_CONFIG["PORT"],
                         user=ns.MODELSEA_CK_CONFIG["USER"],
                         password=ns.MODELSEA_CK_CONFIG["PASS"],
                         database=ns.MODELSEA_CK_CONFIG["NAME"],
                         settings={'use_client_time_zone': True},
                         send_receive_timeout=20)
    return ck_client


def get_cache_pool():
    """获取Redis连接池"""
    return redis.ConnectionPool(host=ns.REDIS_CONFIG["HOST"], port=ns.REDIS_CONFIG["PORT"],
                                password=ns.REDIS_CONFIG["PASS"])


def load_predata(before_date=None):
    """加载准备数据"""
    existing_predata = glob.glob(os.path.join(ns.PREDATA_PATH, "predata_*.dat"))
    if len(existing_predata) == 0:
        logger.error(">>    没有找到任何 predata.")
        return None
    if before_date is not None:
        predata_filename_before_date = sorted(
            [t for t in existing_predata if t <= os.path.join(ns.PREDATA_PATH, f"predata_{before_date}.dat")])
        if len(predata_filename_before_date) > 0:
            latest_predata_filename = predata_filename_before_date[-1]
        else:
            latest_predata_filename = sorted(existing_predata)[-1]
    else:
        latest_predata_filename = sorted(existing_predata)[-1]
    logger.info(f">>   读取predata: {latest_predata_filename}.")

    with open(latest_predata_filename, "rb") as f:
        data = pickle.load(f)
    return data


def delete_data_in_ck(ck_client, table_name, cond_str):
    """从ClickHouse中删除数据"""
    ck_client.execute(f"ALTER TABLE {table_name} DELETE WHERE {cond_str}")


def read_dataframe_from_ck(ck_client, sql):
    """从ClickHouse中读取数据"""
    return ck_client.query_dataframe(sql, settings={'use_client_time_zone': True})


def get_ck_table_type_dict(ck_client, table_name):
    """获取ClickHouse中指定表格的类型"""
    sql = f"SELECT name, type FROM system.columns WHERE table='{table_name}';"
    df = read_dataframe_from_ck(ck_client, sql)
    df = df.set_index("name")
    type_dict = df.to_dict('dict')['type']
    return type_dict


def write_dataframe_to_ck(ck_client, table_name, df):
    """往ClickHouse中写入数据"""
    type_dict = get_ck_table_type_dict(ck_client, table_name)

    for col in df.columns:
        col_type = type_dict[col]
        if 'Date' in col_type:
            df[col] = pd.to_datetime(df[col])
        elif 'Int' in col_type:
            df[col] = df[col].astype('int')
        elif 'Float' in col_type:
            df[col] = df[col].astype('float')
        elif 'String' == col_type:
            df[col] = df[col].astype('str').fillna('')

    columns_str = ','.join(df.columns)
    df_data = df.to_dict("records")
    ck_client.execute(f"INSERT INTO {table_name} ({columns_str}) VALUES", df_data, types_check=True)
