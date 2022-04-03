from flask import (
    Flask,
    jsonify,
)

from auth_center import OpenIDConnect

app = Flask(__name__)
OpenIDConnect(app=app)


@app.route('/hello', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def hello():
    data = {
        "server": "use keyload",
        "status": "working",
        "data": "Hello"
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
