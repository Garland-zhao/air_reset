import hashlib
import time

from my_celery import app


@app.task
def compute_hash(value, target):
    """计算value计算范围内第一个包含target的hash

    :param value: int
    :param target: str
    :return:
    """
    time.sleep(20)
    for i in range(1, value):
        md = hashlib.md5()
        md.update(f'{i}'.encode('utf-8'))  # 制定需要加密的字符串
        if str(target) in md.hexdigest():
            return i
    return None


if __name__ == '__main__':
    foo = compute_hash
    status, res = foo(10000, 'abc')
    print(status)
    print(res)
