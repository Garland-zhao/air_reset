import time

from my_celery_demo import my_add
from alive_progress.styles import showtime

showtime()

# 调用任务后返回的一个 AsyncResult 实例：
# res = my_add.delay(2, 4)
#
# 查看任务状态
# task_status = res.ready()
#
# print(task_status, type(task_status))
# print(dir(res))
# while not task_status:
#     task_status = res.ready()
#     print(task_status)
#     time.sleep(1)
