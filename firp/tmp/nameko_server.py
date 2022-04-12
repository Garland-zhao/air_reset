# nameko_server.py
from nameko.rpc import rpc


class Hello_service:
    name = "hello_service"  # 服务名称

    @rpc  # 标记点入口
    def hello(self, data):
        print(data)
        return "Hello, {}!".format(data)


class Hello_service01:
    name = "hello_service01"

    @rpc
    def hello01(self, data):
        print(data)
        return "Hello, {}!".format(data)

# 启动命令(所在文件目录):
#      1. nameko run nameko_server
#      2. nameko run nameko_server --broker amqp://RabbitMq_username:RabbitMq_password@主机地址