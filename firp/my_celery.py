from __future__ import absolute_import  # 防止重名celery 文件
from celery import Celery
from config import CELERY_NAME
from config import BROKER_URI
from config import BACKEND_URI
from config import INCLUDE_TASK

app = Celery(
    CELERY_NAME,
    broker=BROKER_URI,
    backend=BACKEND_URI,
    include=INCLUDE_TASK
)

