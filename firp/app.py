import sys
from flask import Flask
from all_tasks import *

app = Flask(__name__)


@app.route('/compute_hash/<value>')
def get_compute_hash(value):
    print('compute_value: ', value)
    task_name = 'compute_hash'
    task_engine = getattr(sys.modules[__name__], task_name)
    task = task_engine.delay(int(value), 'abc')
    return task.id


@app.route('/task/status/<task_id>')
def get_task_status(task_id):
    print('task_id: ', task_id)
    task_name = 'compute_hash'
    task_engine = getattr(sys.modules[__name__], task_name)
    task = task_engine.AsyncResult(task_id)
    print(dir(task))

    return task.status


if __name__ == '__main__':
    app.run(debug=True)
