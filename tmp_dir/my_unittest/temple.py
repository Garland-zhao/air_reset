# 保存为temple.py

# coding:utf-8
# 作者：上海-悠悠 QQ交流群：588402570

def zhifu():
    '''假设这里是一个支付的功能,未开发完
    支付成功返回：{"result": "success", "reason":"null"}
    支付失败返回：{"result": "fail", "reason":"余额不足"}
    reason返回失败原因
    '''
    pass


def zhifu_statues():
    '''根据支付的结果success or fail，判断跳转到对应页面'''
    result = zhifu()
    print(result)
    try:
        if result["result"] == "success":
            return "支付成功"
        elif result["result"] == "fail":
            print("失败原因：%s" % result["reason"])
            return "支付失败"
        else:
            return "未知错误异常"
    except:
        return "Error, 服务端返回异常!"


class MYA:
    def __init__(self, a):
        self.a = a

    @staticmethod
    def foo_1(a, b):
        return a + b

    @classmethod
    def foo_2(cls, a, b):
        return a - b

    @property
    def foo_3(self):
        return self.a

    @staticmethod
    def foo_4(a, b):
        res = MYA.foo_1(a, b)
        return MYA.foo_2(res, 5)
