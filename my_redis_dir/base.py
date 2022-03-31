from redis import (
    StrictRedis,
    ConnectionPool,
)

REDIS_CONFIG = {
    'host': '127.0.0.1',
    'port': 6379,
    'password': None,
    'db': 0,
    'decode_responses': False,
    'max_connections': 20,
    'socket_timeout': 5
}


class Singleton(type):
    """单例方法类, 通过__call__来实现单例"""

    def __init__(cls, name, bases, attrs):
        super(Singleton, cls).__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance


class RedisClient(metaclass=Singleton):
    """Redis连接, 通过Singleton实现单例"""

    def __init__(self):
        redis_pool = ConnectionPool(**REDIS_CONFIG)
        self.client = StrictRedis(connection_pool=redis_pool)


class MyRedisQuery(RedisClient):
    """查询Redis的类"""

    # ===============str 相关的方法==================
    """
    set(name, value, ex=None, px=None, nx=False, xx=False, keepttl=False)
    ex：设置过期时间(秒)
    px：设置过期时间(毫秒)
    nx：如果设置为True，则只有name不存在时，当前set操作才会执行，如果存在就不做操作
    xx：如果设置为True，则只有name存在时，当前set操作才执行，值存在则修改，若不存在则不做设置新值操作
    """
    def set_str(self, key, value):
        self.client.set(key, value)
        self.client.set(key, value, ex=None, px=None, nx=False, xx=F)


    def get_str(self, key):
        self.client.get(key)

    def get_all_str_keys(self):
        self.client.keys()

    def get_all_str_keys_like(self, key):
        self.client.keys(key)

    def del_str(self, key):
        self.client.delete(key)

    def incr_str(self, key):
        """该键的值加一, 并返回加一后的值"""
        return self.client.incr(key)

    def incrby_str(self, key, amount=100):
        """该键的值加amount, 并返回添加后的值"""
        return self.client.incrby(key, amount=amount)
        # return self.client.incr(key, amount=amount)  # 效果一样

    def decr_str(self, key):
        return self.client.decr(key)
        # return self.client.incr(key, amount=-1)  # 效果一样

    # ===============hash 相关的方法==================
    def hset_hash(self, name, field, value):
        self.client.hset(name, field, value)

    def hest_hash_with_dict(self, name, dict_data):
        self.client.hset(name, mapping=dict_data)

    def hset_hash_with_2_kinds_data(self, name, field, value, dict_data):
        self.client.hset(name, field, value, mapping=dict_data)

    def hget_hash(self, name, field):
        return self.client.hset(name, field)

    def hget_all_hash_field(self, name):
        return self.client.hgetall(name)

    def hget_all_hash_names_like(self, name):
        return self.client.hkeys(name)

    def hdel_hash_field(self, name, field):
        return self.client.hdel(name, field)

    def hexists_hash_field(self, name, key):
        return self.client.hexists(name, key)

    def hlen_hash_name(self, name):
        return self.client.hlen(name)

    def hincrby_hash_field(self, name, field, amount=10):
        return self.client.hincrby(name, field, amount=amount)

    # list 相关的方法(redis 使用双端链表来实现list)
    """
    lpush+lpop=Stack(栈)
    lpush+rpop=Queue（队列）
    lpush+ltrim=Capped Collection（有限集合）
    lpush+brpop=Message Queue（消息队列）
    rpush+lrpop=Message Queue（消息队列）
    """

    # set
    """
    集合类型也是用来保存多个字符串的元素，但和列表不同的是集合中  
        1. 不允许有重复的元素，
        2.集合中的元素是无序的，不能通过索引下标获取元素，
        3.支持集合间的操作，可以取多个集合取交集、并集、差集。
    """


class MessageQueue:
    """消息队列"""

    def __init__(self, name, namespace='queue'):
        self.client = RedisClient().client
        self.key = f'{namespace}{name}'

    def qsize(self):
        return self.client.llen(self.key)

    def put(self, item):
        self.client.rpush(self.key, item)

    def get(self):
        """返回元素, item"""
        self.client.lpop(self.key)

    def get_wait(self, timeout=None):
        """返回元祖, (self.key, item)"""
        return self.client.blpop(self.key, timeout=timeout)


import redis


class TaskProductionConsumptionModel:
    """生产消费模型, 基于 redis list 数据类型实现"""

    def __init__(self):
        self.rcon = redis.StrictRedis(host='localhost', db=5)
        self.queue = 'task:prodcons:queue'

    def listen_task(self):
        while True:
            task = self.rcon.blpop(self.queue, 0)[1]
            print("Task get", task)


TaskProductionConsumptionModel().listen_task()


class TaskPublishSubscriptionModel:
    """发布订阅模型, 基于 redis pubsub 实现"""

    def __init__(self):
        self.rcon = redis.StrictRedis(host='localhost', db=5)
        self.ps = self.rcon.pubsub()
        self.ps.subscribe('task:pubsub:channel')

    def listen_task(self):
        for i in self.ps.listen():
            if i['type'] == 'message':
                print("Task get", i['data'])


TaskPublishSubscriptionModel().listen_task()

# 在Flask中使用
import redis
import random
import logging
from flask import Flask, redirect

app = Flask(__name__)

rcon = redis.StrictRedis(host='localhost', db=5)
prodcons_queue = 'task:prodcons:queue'
pubsub_channel = 'task:pubsub:channel'


@app.route('/')
def index():
    html = """
        <br>
        <center><h3>Redis Message Queue</h3>
        <br>
        <a href="/prodcons">生产消费者模式</a>
        <br>
        <br>
        <a href="/pubsub">发布订阅者模式</a>
        </center>
        """
    return html


@app.route('/prodcons')
def prodcons():
    elem = random.randrange(10)
    rcon.lpush(prodcons_queue, elem)
    logging.info(f"lpush {prodcons_queue} -- {elem}")
    return redirect('/')


@app.route('/pubsub')
def pubsub():
    ps = rcon.pubsub()
    ps.subscribe(pubsub_channel)
    elem = random.randrange(10)
    rcon.publish(pubsub_channel, elem)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
