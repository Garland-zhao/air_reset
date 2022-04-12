# delay
from tasks import add

add.delay(arg1, arg2, kwarg1='x', kwarg2='y')
add.delay(*args, **kwargs).apply_async(args, kwargs)

# apply_async
task.apply_async(args=[arg1, arg2], kwargs={'kwargs': 'x', 'kwargs': 'y'})
tasks.apply_async((arg,), {'kwarg': value})
# 从现在起10秒内执行
tasks.apply_async(countdown=10)
# 从现在起10秒内执行,使用指定eta
tasks.apply_async(eta=now + timedelta(seconds=10))
# 从现在起一分钟后执行，但在2分钟后过期
tasks.apply_async(countdown=60, expires=120)
# 在2天后到期，设置使用datetime对象
T.apply_async(expires=now + timedelta(days=2))

# send_task：任务未在当前进程中注册
app.send_task('任务', args=[arg, ], queue='default')

# signature用于传递任务调用签名的对象(例如通过网络发送),并且它们也支持calling api
task.s(arg1, arg2, kwarg1='x', kwargs2='y').apply_async()
