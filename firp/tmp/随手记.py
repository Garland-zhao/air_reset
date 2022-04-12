"""
docker 部署 RabbitMQ

拉取镜像
docker pull rabbitmq:management

运行容器
docker run -d --hostname my-rabbit --name rabbit -p 15672:15672 -p 5672:5672 rabbitmq:management

若需要设置用户名&密码
docker run -d --hostname my-rabbit --name rabbit -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password -p 15672:15672 -p 5672:5672 rabbitmq:management

"""