from nameko.standalone.rpc import ClusterRpcProxy

CONFIG = {'AMQP_URI': "amqp://guest:guest@192.168.110.129"}


def compute():
    with ClusterRpcProxy(CONFIG) as rpc:
        rpc.hello_service.hello()


if __name__ == '__main__':
    compute()
