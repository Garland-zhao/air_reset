import json
from pprint import pp
import requests as req
from base64 import b64encode

# 开发环境
# kc_uri = 'https://keycloak.deepredai.com'
# realm = 'new_master_realm'
# FE_client = 'firp'
# client = 'test_client'
# client_secret = "wKiwtwaDpOxywZEjrVoElPYhs3g4iLIb"
# username = "user_1"
# pwd = "1234"

kc_uri = 'https://firp.deepredai.com'
realm = 'master'
FE_client = 'firp'
client = 'firp_be'
client_secret = "kyLTNCVM0K6JTI7AqgWEMCuFCfbASWx2"
username = "firp"
pwd = "1234"




def get_new_token(show_token_info=False, show_access_token=False):
    access_token = ""
    req_data = {
        "client_id": FE_client,
        "username": username,
        "password": pwd,
        "grant_type": "password",
    }
    token_uri = f"{kc_uri}/auth/realms/{realm}/protocol/openid-connect/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", }
    resp = req.post(token_uri, data=req_data, headers=headers)
    if resp.status_code != 200:
        print('get new token error', resp.text)
    else:
        data = json.loads(resp.text)
        if show_token_info:
            print('token info ==\n')
            pp(data)
        access_token = data.get('access_token')
        if show_access_token:
            print("\naccessToken == \n", access_token)
    return access_token


def check_token_active(access_token, show_active=False, show_token_info=False):
    uri = f"{kc_uri}/auth/realms/{realm}/protocol/openid-connect/token/introspect"
    req_json = {
        'token': access_token,
        # 'token_type_hint': "access_token",  # This is not necessary
    }
    headers = {'Content-type': 'application/x-www-form-urlencoded'}

    # auth_method = "client_secret_basic"
    # auth_method = "bearer"
    auth_method = "client_secret_post"

    if auth_method == 'client_secret_basic':
        basic_auth_string = '%s:%s' % (client, client_secret)
        basic_auth_bytes = bytearray(basic_auth_string, 'utf-8')
        headers['Authorization'] = 'Basic %s' % b64encode(basic_auth_bytes).decode('utf-8')
    elif auth_method == 'client_secret_post':
        req_json['client_id'] = client
        if client_secret is not None:
            req_json['client_secret'] = client_secret
    elif auth_method == 'bearer':
        print('auth method bearer')
        headers['Authorization'] = 'Bearer %s' % token
    else:
        raise ValueError('No matched auth_method')

    resp = req.post(uri, data=req_json, headers=headers)
    if resp.status_code != 200:
        print('\ncheck token error', resp.text)
    else:
        data = json.loads(resp.text)
        if show_token_info:
            print('\n check token active response ==\n')
            pp(data)
        active = data.get('active', None)
        if show_active:
            print(f'\n\ntoken active is {active}\n')
        return active


def get_user_info(access_token, show_user_info=False):
    userinfo = ""
    header = {
        "Authorization": "Bearer " + access_token
    }
    userinfo_uri = f'{kc_uri}/auth/realms/{realm}/protocol/openid-connect/userinfo'

    resp = req.get(userinfo_uri, headers=header)
    if resp.status_code != 200:
        print('get user info error', resp.text)
    else:
        userinfo = json.loads(resp.text)

    if show_user_info:
        print('userinfo ==\n')
        pp(userinfo)

    return userinfo


if __name__ == '__main__':
    token = get_new_token(show_token_info=True, show_access_token=True)

    check_token_active(token, show_active=True, show_token_info=True)

    get_user_info(token, show_user_info=True)
