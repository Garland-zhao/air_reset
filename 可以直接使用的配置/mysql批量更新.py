# -*- coding: utf-8 -*-
"""
@Time ： 2022/3/31 16:11
@Auth ： ZhaoFan
@File ：mysql批量更新.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import pymysql
from datetime import datetime

MYSQL_CONFIG = {
    'user': 'root',
    'password': 'devmysql',
    'host': '172.19.18.141',
    'port': 50001,
    'database': 'zhaofan',  # 数据库名
}
db = pymysql.connect(host='172.19.18.141',
                     port=50001,
                     user='root',
                     password='devmysql',
                     database='zhaofan')
cur = db.cursor()


def insert_data():
    for i in range(50):
        sql = """INSERT INTO `zhaofan`.`tmp_user` (`sub`, `data`, `update_time`) 
        VALUES ('8016f9f3-6821-42f3-9696-5a2da1469370', 'zhaofan', '2022-02-21 11:00:58')"""
        cur.execute(sql)

    db.commit()


def update_data():
    FUND_SIMILARITY_TABLE = 'tmp_user'
    VERIF_FIELD = 'data'
    TIME_FIELD = 'update_time'

    data_str = ""
    ids = []
    update_data_list = []
    update_time_list = []
    for i in range(1, 50):
        ids.append(i)
        data_str += f'WHEN {i} THEN %s '
        update_data_list.append(f'{i}_pwd')
        update_time_list.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    ids = tuple(ids)
    update_data_list.extend(update_time_list)

    sql = f"""UPDATE {FUND_SIMILARITY_TABLE} SET 
    {VERIF_FIELD} = CASE id {data_str} END,
    {TIME_FIELD} = CASE id {data_str} END 
    WHERE id IN {ids}"""
    cur.execute(sql, update_data_list)
    db.commit()


if __name__ == '__main__':
    # insert_data()
    update_data()
