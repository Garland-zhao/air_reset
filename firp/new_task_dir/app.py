from my_celery_demo import my_add

# 调用任务后返回的一个 AsyncResult 实例：
res = my_add.delay(2, 4)

# 查看任务状态
task_status = res.ready()

a = 1
b = 1
