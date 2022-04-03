import os

# base OpenId Connect config
OIDC_CONFIG = {
    'MAX_CACHE_SIZE': os.getenv('MAX_CACHE_SIZE', 1000),
    'CACHE_TTL': os.getenv('CACHE_TTL', 3600 * 24 * 3),
    'OIDC_SCOPES': os.getenv('OIDC_SCOPES', ['openid', 'email', 'profile']),  # openid must be in OIDC_SCOPES
    'SECRET_KEY': os.getenv('SECRET_KEY', 'my_salt'),  # create signers using the Flask secret key
    'MAX_EXP': os.getenv('MAX_EXP', 3600 * 24),  # must re-login after 24 hours
    'CALLBACK_ROUTE': os.getenv('CALLBACK_ROUTE', '/oidc_callback'),  # keycloak回调路径
    'CALLBACK_ENDPOINT': os.getenv('CALLBACK_ENDPOINT', '_oidc_callback'),  # keycloak回调路径的endpoint
    'CALLBACK_ERROR_ENDPOINT': os.getenv('CALLBACK_ERROR_ENDPOINT', '_oidc_error'),  # keycloak回调路径的endpoint
    'LOGIN_PATH': os.getenv('LOGIN_PATH', '/login'),
    'LOGIN_ENDPOINT': os.getenv('LOGIN_ENDPOINT', '_login'),
    'LOGOUT_PATH': os.getenv('LOGOUT_PATH', '/logout'),
    'LOGOUT_ENDPOINT': os.getenv('LOGOUT_ENDPOINT', '_logout'),
    'HOME_PAGE': os.getenv('HOME_PAGE', '/hello'),  # redirect this page after login successfully
    'OIDC_ID_TOKEN': os.getenv('OIDC_ID_TOKEN', 'oidc_id_token'),
    'COOKIE_PATH': os.getenv('COOKIE_PATH', '/'),
    'COOKIE_TTL': os.getenv('COOKIE_TTL', 7 * 86400),  # 7 days
    'Extended_Expiration': os.getenv('Extended_Expiration', 60 * 60),  # extend token exp when refresh fail
    'PAYLOAD_ITEMS': os.getenv('PAYLOAD_ITEMS'),
    'OIDC_ID_TOKEN_COOKIE_SECURE': os.getenv('OIDC_ID_TOKEN_COOKIE_SECURE', False),
    'OIDC_REQUIRE_VERIFIED_EMAIL': os.getenv('OIDC_REQUIRE_VERIFIED_EMAIL', False),
    'OIDC_RESOURCE_CHECK_AUD': os.getenv('OIDC_RESOURCE_CHECK_AUD', False),  # check token aud
    'OIDC_CLOCK_SKEW': os.getenv('OIDC_CLOCK_SKEW', 60),  # check token iat

}

# keycloak uri config
KC_CONFIG = {
    'KC_AUTH_URI': os.getenv('KC_AUTH_URI', 'https://keycloak.deepredai.com'),  # keycloak server uri
    'KC_REALMS': os.getenv('KC_REALMS', 'new_master_realm'),  # keycloak realms name
    'KC_CLIENT_ID': os.getenv('KC_CLIENT_ID', 'test_client'),  # keycloak client name
    'KC_CLIENT_SECRET': os.getenv('KC_CLIENT_SECRET', 'wKiwtwaDpOxywZEjrVoElPYhs3g4iLIb'),  # keycloak client secret
}

