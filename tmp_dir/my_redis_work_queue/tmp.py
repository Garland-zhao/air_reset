import pandas as pd
from utils import RedisClient
from utils import RedisQueue
import logging

logger = logging.Logger(__name__)


class SimilarityTask:
    """
    基金相似相计算任务
    """
    TASK_QUEUE = None  # 相似性计算任务队列
    TASK_QUEUE_NAME = 'task:similarity'

    USER_QUEUE = None  # 用户&任务队列

    @classmethod
    def task_key(cls, ticker, compute_date, size):
        """生成计算任务的key
        """
        return f"{ticker}:{compute_date}:{size}"

    @classmethod
    def task_to_compute_queue(cls):
        """任务队列的单例"""
        if not cls.TASK_QUEUE:
            cls.TASK_QUEUE = RedisQueue(cls.TASK_QUEUE_NAME)
        return cls.TASK_QUEUE

    @classmethod
    def task_to_user_queue(cls):
        """用户&任务队列的单例"""
        if not cls.USER_QUEUE:
            cls.USER_QUEUE = RedisClient().conn
        return cls.USER_QUEUE

    @classmethod
    def add_task_to_compute(cls, task):
        """添加新的task到任务队列"""
        # 去重添加
        cls.task_to_compute_queue().put(task, duplicate=False)

    @classmethod
    def add_task_to_user(cls, task, sub):
        """添加新的user&task到用户&任务队列"""
        cls.task_to_user_queue().set(f'{sub}:{task}', 1)

    @classmethod
    def next_task(cls):
        return cls.task_to_compute_queue().get_nowait()

    @classmethod
    def clean_user_task(cls, task):
        """从user & task 队列中清除已完成的任务"""
        cls.task_to_user_queue().delete(f'*:{task}')

    @classmethod
    def current_user_task_exist(cls, sub):
        """检索当前用户执行中的任务"""
        return cls.task_to_user_queue().keys(f'{sub}:*')

    @classmethod
    def generate_task(cls, ticker, compute_date, size, sub):
        task = cls.task_key(ticker, compute_date, size)  # 创建task_key
        cls.add_task_to_user(task, sub)  # 添加 task 到当前用户任务列表
        cls.add_task_to_compute(task)  # 添加 task 到相似性计算任务列表


class SimilarityPortCache(RedisClient):
    """
    相似性组合计算结果缓存
    """
    DATA_TYPES = [
        'port',  # 相似性组合
        'ind',  # 行业分配
        'ret',  # 收益
    ]

    def set_data(self, key, field, data):
        """save data into reids"""
        self.conn.hset(key, field, data)

    def get_date(self, ticker, compute_date, size, port_id):
        key = f"{ticker}:{compute_date}:{size}:{port_id}"
        return self._get_data(key)

    def _get_data(self, key):
        """从redis中获取结果

        :return: DataFrame
        """
        result = self.conn.hgetall(key)
        if not result:
            logger.warning(f'Similarity has no data with key:{key}')
            return pd.DataFrame()

        # TODO 分类三种结果
        data = []
        for k in result:
            # v = pd.read_pickle(io.BytesIO(result[k]))
            v = pd.read_json(result[k])  # TODO 测试用json保存value
            k = k.decode('utf8')
            data.append({k: v})

        return pd.DataFrame(data)

    def get_status(self, ticker, compute_date, size):
        """检索目标任务的计算状态"""
        # check done
        key = f'{ticker}:{compute_date}:{size}*'
        result = self.conn.hgetall(key)
        if result:
            return 1


if __name__ == "__main__":
    pass
