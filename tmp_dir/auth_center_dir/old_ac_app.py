from flask import (
    Flask,
    jsonify,
)
from oauth2client.client import OAuth2Credentials

from old_ac import OpenIDConnect

app = Flask(__name__)

oidc = OpenIDConnect()
oidc.init_app(app)


@app.route('/hello', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def hello():
    data = {
        "server": "use keyload",
        "status": "working",
        "data": "Hello"
    }
    key = list(oidc.credentials_store.keys())[0]
    print(key)
    access_token = OAuth2Credentials.from_json(oidc.credentials_store.get(key)).access_token
    print("access_token\n")
    print(access_token)
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
