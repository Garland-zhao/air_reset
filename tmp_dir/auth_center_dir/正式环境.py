import json
from pprint import pp
import requests as req
from base64 import b64encode

# 正式环境
kc_uri = 'https://www.deepredai.com'
realm = 'master'
FE_client = 'firp'
client = 'firp_be'
client_secret = "0myLSCmurCvYdqf5P06ZO6fruFPomWOb"
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
    token = get_new_token(show_token_info=False, show_access_token=True)

    # token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJLZUh1bjR6OExaUVU4ZExjMFZmX1BmTXA0TzRIRHhJenJVWnFEaVJ2Y0w4In0.eyJleHAiOjE2NDQ4MjY1MDUsImlhdCI6MTY0NDgyNDcwNSwiYXV0aF90aW1lIjoxNjQ0ODI0NzA1LCJqdGkiOiJkZWVhN2YyZS1hOWE4LTQwZTItYjc2Mi1iYTFkZWRhMzQ3MDYiLCJpc3MiOiJodHRwczovL3d3dy5kZWVwcmVkYWkuY29tL2F1dGgvcmVhbG1zL21hc3RlciIsInN1YiI6ImIzYzVlYjZkLTI2MTYtNDNhOS1hMWZhLTZmODg4NjJjM2Y4YyIsInR5cCI6IkJlYXJlciIsImF6cCI6ImZpcnAiLCJub25jZSI6IjNhNTJmOWY0LWFkM2UtNGE5Ny04M2E4LWY2NDQyNDFjMTUwZiIsInNlc3Npb25fc3RhdGUiOiI1MDU2Zjg4NS05ZGM2LTQ5YTYtYjA0ZS03OWQ0Njk4NTFlNTIiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIuWfuumHkeeglOeptl_ooYzkuJrmjIHku5Nf55Sz5LiH5LiA57qnKOeul-azlSlf6KGM5Lia6YWN572u6ZuG5Lit5pe25bqP5Zu-Iiwi5Z-66YeR56CU56m2X-ihjOS4muaMgeS7k1_nlLPkuIfkuIDnuqco566X5rOVKV_ooYzkuJrphY3nva7ml7bluo_lm74iLCLln7rph5HnoJTnqbZf6KGM5Lia5oyB5LuTX-eUs-S4h-S4gOe6pyjnrpfms5UpX-ihjOS4mumFjee9riJdfSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInNpZCI6IjUwNTZmODg1LTlkYzYtNDlhNi1iMDRlLTc5ZDQ2OTg1MWU1MiIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2FyZHNfYWNjZXNzX2xpc3QiOlsi5Z-66YeR56CU56m2X-ihjOS4muaMgeS7k1_nlLPkuIfkuIDnuqco566X5rOVKV_ooYzkuJrphY3nva7pm4bkuK3ml7bluo_lm74iLCLln7rph5HnoJTnqbZf6KGM5Lia5oyB5LuTX-eUs-S4h-S4gOe6pyjnrpfms5UpX-ihjOS4mumFjee9ruaXtuW6j-WbviIsIuWfuumHkeeglOeptl_ooYzkuJrmjIHku5Nf55Sz5LiH5LiA57qnKOeul-azlSlf6KGM5Lia6YWN572uIl0sInByZWZlcnJlZF91c2VybmFtZSI6InpoYW5na2FpIn0.tit4aZC-WNxuC8jkvg5vlfCVUn96EhN6vH8bnOuqHp9eFIXNL3gk66-Tmzg4CkiVxxFtHB3F2O_x4DpF71XxWJ4oXOHCCCWcL5NUv0vt3OInNFhEtaBkBQ8reKUP9DoHjXOh_JDyTj1ns2P0HyMcoOkhksmHMAeSOtNCR-7OwaZOuQjohlbYANjGur8USvo8cFQ6rUBcrILQ2MCf3_tjWl0LlKzs09BKRBQxxrOicp7p--OR9GbxFm4yJ0ekWmJHnt0LNf2u-Hx5RYAk8D-rj1V3L_jOpZ8f-QGfClnlvxHJnAw9gpqoZXADae-r4ojSgdpl0GN5c0wN-pCGgZCH4g"
    check_token_active(token, show_active=True, show_token_info=True)

    get_user_info(token, show_user_info=True)

    result = {'exp': 1644826471,
 'iat': 1644824671,
 'jti': '2fd51bf1-691d-4ab7-a978-db42792f0d6b',
 'iss': 'https://www.deepredai.com/auth/realms/master',
 'sub': 'c32c1096-a00d-4bab-9b34-ce4f5753b42c',
 'typ': 'Bearer',
 'azp': 'firp',
 'session_state': 'db4db519-fb25-453b-aabe-9e80525ec91a',
 'name': 'firp_first_name frip_last_name',
 'given_name': 'firp_first_name',
 'family_name': 'frip_last_name',
 'preferred_username': 'firp',
 'email': 'firp@deepredai.com',
 'email_verified': False,
 'acr': '1',
 'allowed-origins': ['*'],
 'realm_access': {'roles': ['基金研究_行业持仓_申万一级(算法)_行业配置集中时序图',
                            '基金研究_行业持仓_申万一级(算法)_行业配置时序图',
                            '基金研究_行业持仓_申万一级(算法)_行业配置']},
 'scope': 'profile email',
 'sid': 'db4db519-fb25-453b-aabe-9e80525ec91a',
 'cards_access_list': ['基金研究_行业持仓_申万一级(算法)_行业配置集中时序图',
                       '基金研究_行业持仓_申万一级(算法)_行业配置时序图',
                       '基金研究_行业持仓_申万一级(算法)_行业配置'],
 'client_id': 'firp',
 'username': 'firp',
 'active': True}

