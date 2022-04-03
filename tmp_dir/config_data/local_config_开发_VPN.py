# ------------------------------AC---------------------------------------------
# AC基础环境变量
OIDC_CONFIG = {
    'MAX_CACHE_SIZE': 1000,
    'CACHE_TTL': 60 * 10,  # 默认缓存token时间,超时后会从KC重新同步token
    'OIDC_ID_TOKEN': 'oidc_id_token',
    'SKIP_AUTH': False,  # 系统检查token的总开关
    'SKIP_AUTH_METHODS': 'OPTIONS,',  # 跳过auth的method白名单
    'SKIP_AUTH_IP': False,  # 跳过auth的host白名单
    'SKIP_AUTH_PATH': False,  # 跳过auth的path白名单
    'SKIP_AUTH_IN_HEADER': 'skipAC',  # 根据header判断请求跳过auth
}

# KC开发环境
KC_CONFIG = {
    'KC_AUTH_URI': "https://keycloak.deepredai.com",
    'KC_REALMS': "new_master_realm",
    'KC_CLIENT_ID': "test_client",
    'KC_CLIENT_SECRET': "wKiwtwaDpOxywZEjrVoElPYhs3g4iLIb",
    'KC_CARDS_ACCESS': "cards_access_list",
    'REQUIRE_ACCESS': "card"
}

# -----------------------------FIRP--------------------------------------------
# firp 数据库
FIRP_MYSQL_CONFIG = {
    'ENGINE': 'mysql',
    'DRIVER': 'pymysql',
    'USER': 'root',
    'PASSWORD': 'devmysql',
    'HOST': '172.19.18.141',
    'PORT': 50001,
    'NAME': 'zhaofan',  # 数据库名
}

# 相似性组合计算结果缓存
FIRP_REDIS_CONFIG = {
    'host': '172.19.18.141',
    'port': 50004,
    'password': "V9Ncd3AWtnxVI8S",
    'db': 12,
    'decode_responses': False,
    'max_connections': 20,
    'socket_timeout': 5
}

# DataSea
DATASEA_CONFIG = {
    'ENGINE': 'mysql',
    'DRIVER': 'pymysql',
    'USER': 'readuser',
    'PASSWORD': 'kAldMZgtX3pTcZj',
    'HOST': '172.19.18.134',
    'PORT': '13003',
    'NAME': 'datasea',
}

# JY
JY_DB_CONFIG = {
    'ENGINE': 'mysql',
    'DRIVER': 'pymysql',
    'USER': "readuser",
    'PASSWORD': "LxkN3Lh1HSLf",
    'HOST': "172.19.18.132",
    'PORT': "13006",
    'NAME': "jydb",
}

# Redis
REDIS_CONFIG = {
    'host': '172.19.18.133',
    'port': 13035,
    'password': "V9Ncd3AWtnxVI8S",
    'db': 0,
    'decode_responses': False,
    'max_connections': 20,
    'socket_timeout': 5
}
REDIS_KEY_EXPIRATION_TIME = 3600

# InfluxDB
INFLUX_CONFIG = {
    'host': "172.19.18.134",
    'port': 13001,
    'username': "readuser",
    'password': "q6EsWaVTwmkE",
    'database': "jyrealtime",
    'pool_size': 20,
    'retries': 3
}

# ClickHouse
CK_CONFIG = {
    "host": "172.19.18.137",
    "port": 30002,
    "user": "appuser",
    "password": "0alVyIO9uTcdYMD",
    "database": "modelsea"
}
