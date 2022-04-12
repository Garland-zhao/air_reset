import os
CELERY_NAME = 'celery_demo_zhao'
BROKER_URI = os.getenv('BROKER_URI', 'amqp://guest:guest@127.0.0.1:5672')
BACKEND_URI = os.getenv('BROKER_URI', 'redis://:V9Ncd3AWtnxVI8S@localhost:6379/0')

# TODO 这里需要在项目启动前动态加载
INCLUDE_TASK = ['task']
