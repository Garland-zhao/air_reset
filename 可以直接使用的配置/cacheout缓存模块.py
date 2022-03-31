from cacheout import Cache
import time


# Cache 为类似dict的键值对存储
# 可以设置最大存储长度和默认过期时间(秒)
def learn_cache():
    token_cache = Cache(maxsize=1000, ttl=10)

    token_cache.set('key_1', 'value1')
    get_1 = token_cache.get('key_1')
    print('get_1', get_1)
    time.sleep(3)
    token_cache.set('key_2', 'value2', ttl=15)
    get_2 = token_cache.get('key_2')
    print('get_2', get_2)

    time.sleep(7)
    get_1 = token_cache.get('key_1')
    print('get_1', get_1)
    get_2 = token_cache.get('key_2')
    print('get_2', get_2)

    time.sleep(3)
    get_2 = token_cache.get('key_2')
    print('get_2', get_2)

    time.sleep(5)
    get_2 = token_cache.get('key_2')
    print('get_2', get_2)


if __name__ == '__main__':
    learn_cache()
