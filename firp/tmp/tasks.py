# tasks.py
from celery import Celery

app = Celery(
    'tasks',  # 当前模块的名字
    broker='amqp://guest@localhost:5672//'  # 消息队列的url
)


@app.task
def add(x, y):
    return x + y
