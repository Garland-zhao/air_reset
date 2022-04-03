from redis import StrictRedis
from redis import ConnectionPool

from common.utils import Singleton

REDIS_CONFIG = {
    # 'host': '172.19.18.133',
    'host': '127.0.0.1',
    'port': 6379,
    # 'password': "V9Ncd3AWtnxVI8S",
    'db': 0,
    'decode_responses': False,
    'max_connections': 20,
    'socket_timeout': 5
}


class RedisClient(metaclass=Singleton):

    def __init__(self):
        redis_pool = ConnectionPool(**REDIS_CONFIG)
        self.conn = StrictRedis(connection_pool=redis_pool)


class RedisQueue:
    def __init__(self, name, namespace='queue'):
        self.__db = RedisClient().conn
        self.key = '%s:%s' % (namespace, name)

    def qsize(self):
        return self.__db.llen(self.key)  # 返回队列里面list内元素的数量

    def put(self, item, duplicate=True):
        if duplicate:
            self.__db.rpush(self.key, item)
        elif item.encode('utf-8') not in self.__db.lrange(self.key, 0, -1):
            self.__db.rpush(self.key, item)  # 添加新元素到队尾

    def get_wait(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.__db.blpop(self.key, timeout=timeout)
        return item

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__db.lpop(self.key)
        return item
