from flask import Flask, request
from flask_restplus import (
    Resource,
    Api,
    reqparse,
    fields,

)

app = Flask(__name__)
api = Api(app)

todos = {}
API_RESPONSE_TEMPLATE = {
    'code': 200,
    'msg': 'ok',
    'data': {}  # api return result data
}

parser = reqparse.RequestParser()
parser.add_argument('rate', type=int)  # parser作为全局对象使用
# args = parser.parse_args()  # args is a dict

model = api.model(
    'Model',
    {'task': fields.String,
     'uri': fields.Url('todo_ep')}
)


class TodoDao:
    def __init__(self, todo_id, task):
        self.todo_id = todo_id
        self.task = task
        self.status = 'active'  # This field will not be sent in the response


@api.route('/todo')
class Todo(Resource):
    @api.marshal_with(model)
    def get(self, **kwargs):
        return TodoDao(todo_id='my_todo', task='faker task')


@api.route('/<string:todo_id>', endpoint='todo_ep')
class TodoSimple(Resource):
    def get(self, todo_id):
        args = parser.parse_args(strict=True)  # args is a dict
        print('args', args)
        return {todo_id: todos[todo_id]}

    def post(self, todo_id):
        if todo_id in todos:
            return {'msg': 'Duplicate data'}
        else:
            value = request.form['data']
            todos[todo_id] = request.form['data']

            return {'msg': f'save {todo_id} with {value}'}

    def put(self, todo_id):
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}


@api.route('/todo1')
class Todo1(Resource):
    def get(self):
        # Default to 200 OK
        return {'task': 'Hello world'}


@api.route('/todo2')
class Todo2(Resource):
    def get(self):
        # Set the response code to 201
        return {'task': 'Hello world'}, 201


@api.route('/todo3')
class Todo3(Resource):
    def get(self):
        # Set the response code to 201 and return custom headers
        return {'task': 'Hello world'}, 201, {'Etag': 'some-opaque-string'}


@api.route('/todo4')
class Todo4(Resource):
    def get(self):
        # try response template
        return API_RESPONSE_TEMPLATE


if __name__ == '__main__':
    app.run(debug=True)
