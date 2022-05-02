from celery import Celery

# 初始化, 并使用RabbitMQ作为分发消息中间人
app = Celery(
    'task_demo',
    broker='amqp://root:PfFhtpwLDLzDjNg@192.168.2.9:50008//',
    backend='redis://:ILWKzuytVjOfNv7@192.168.2.9:50006/6'
)


# app = Celery('hello', broker='redis://:V9Ncd3AWtnxVI8S@localhost:6379/0')  # 使用redis


# 定义一个任务, 该任务的内容是print Hello Garland
@app.task
def my_add(x, y):
    return x + y


@app.task
def add_new_similar_task(task):
    compute_date = task['compute_date']
    ticker = task['ticker']
    size = task['size']
    white_id = task['white_id']


"""
高可用
如果出现丢失连接或连接失败，工作单元（Worker）和客户端会自动重试，
并且中间人通过 主/主 主/从 的方式来进行提高可用性。

快速
单个 Celery 进行每分钟可以处理数以百万的任务，
而且延迟仅为亚毫秒（使用 RabbitMQ、 librabbitmq 在优化过后）

灵活
Celery 的每个部分几乎都可以自定义扩展和单独使用，
例如自定义连接池、序列化方式、压缩方式、日志记录方式、任务调度、生产者、消费者、中间人（Broker）等。
"""


@app.task
def add_new_similar_task(task_key):
    compute_date = task_key
