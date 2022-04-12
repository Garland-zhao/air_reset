from nameko.rpc import rpc


class HelloServer:
    name = "hello_service"

    @rpc
    def hello(self):
        print("hello world")
