from tmp import SimilarityTask
from tmp import SimilarityPortCache
from utils import RedisQueue
from utils import RedisClient
import time
import json


# 下发计算任务
def generate_task(ticker, compute_date, size, sub):
    # 创建task_key
    task = SimilarityTask.task_key(ticker, compute_date, size)
    # 添加 task 到当前用户任务列表
    SimilarityTask.add_task_to_user(task, sub)
    # 添加 task 到相似性计算任务列表
    SimilarityTask.add_task_to_compute(task)


# 查看任务队列
def get_task_from_task_queue():
    while 1:
        result = SimilarityTask.next_task()
        if not result:
            break
        print("get_data_from_task_queue: task {}".format(result))
        time.sleep(1)


# 查看user 队列
def get_all_user_task():
    keys = RedisClient().conn.keys()
    print('keys:', keys)


# 查看current_user task exist
def get_task_from_user_queue(sub, task):
    result = SimilarityTask.current_user_task_exist(sub, task)
    print('当前用户任务状态:', result)


# 保存相似性结果数据到redis
def set_data_into_redis(key):
    r = SimilarityPortCache()
    data = [
        {
            'fund_code': '184688.OF',
            'fund_name': '南方开元封闭',
            'weight': 0.4,
        },
        {
            'fund_code': '184689.OF',
            'fund_name': '鹏华普惠封闭',
            'weight': 0.4,
        },
        {
            'fund_code': '184690.OF',
            'fund_name': '长盛同益封闭',
            'weight': 0.2,
        },
    ]
    data = json.dumps(data)
    print('data_type:', type(data))
    for field in SimilarityPortCache.DATA_TYPES:
        r.set_data(key, field, data)


# 从redis中读取相似性结果数据
def get_data_from_redis(key):
    r = SimilarityPortCache()
    result = r._get_data(key)
    print('get similarity_cache:', result)


if __name__ == '__main__':
    ticker = '001380'
    compute_date = '2022-02-15'
    size = 7
    key = f'{ticker}:{compute_date}:{size}'
    sub_1 = '8016f9f3-6821-42f3-9696-5a2da1469371'
    sub_2 = '8016f9f3-6821-42f3-9696-5a2da1469372'

    # step_1: 生成2个user_task 和 1个compute_task
    generate_task(ticker, compute_date, size, sub_1)
    generate_task(ticker, compute_date, size, sub_2)
    # test step_1
    get_task_from_task_queue()
    get_all_user_task()
    get_task_from_user_queue(sub_1, key)
    get_task_from_user_queue(sub_2, key)

    # # step2: 保存相似性结果和读取
    # set_data_into_redis(key)
    # get_data_from_redis(key)
