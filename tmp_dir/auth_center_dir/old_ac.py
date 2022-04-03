import json
import time
import base64
import hashlib
import logging
import calendar
import httplib2
import traceback

from copy import copy
from cacheout import Cache
from urllib.parse import (
    urlencode,
    urljoin,
    urlparse,
)
from base64 import urlsafe_b64encode, urlsafe_b64decode

from flask import (
    g,
    request,
    url_for,
    jsonify,
    redirect,
)
from oauth2client.clientsecrets import TYPE_WEB
from oauth2client.client import (
    flow_from_clientsecrets,
    AccessTokenRefreshError,
    OAuth2Credentials,
)

from itsdangerous import (
    JSONWebSignatureSerializer,
    BadSignature,
    TimedJSONWebSignatureSerializer,
    SignatureExpired,
)
from config import OIDC_CONFIG, KC_CONFIG

logger = logging.getLogger(__name__)


class DummySecretsCache:
    """
    oauth2client secrets cache
    """

    def __init__(self, client_secrets):
        self.secrets_cache = client_secrets

    def get(self, *args, **kwargs):
        return self.secrets_cache


class KCToken:
    def __init__(self, payload=None, cookies_token=None, credentials=None):
        self.payload = payload
        self.cookies_token = cookies_token
        self.credentials = credentials
        self.access_token = None


class Tools:
    cache = None

    @classmethod
    def compute_md5(cls, data):
        if isinstance(data, str):
            data = data.encode('utf8')
        m = hashlib.md5(data)
        return m.hexdigest()

    @staticmethod
    def ttl_cache():
        return Cache(maxsize=OIDC_CONFIG['MAX_CACHE_SIZE'], ttl=OIDC_CONFIG['CACHE_TTL'])


class OpenIDConnect:
    """
    The core OpenID Connect client object.
    """
    BASE_TOKEN_ITEM = [
        'exp',
        'iat',
        'auth_time',
        'jti',
        'sub',
        'typ',
        'session_state',
        'at_hash',
        'sid',
        'cards_access_list',
        'preferred_username'
    ]
    ACCESS = 'cards_access_list'
    REQUIRE_ACCESS = 'cards_access'
    DESTINATION = 'destination'
    check_action_mapping = {
        'cached': 'exp',
        'exp': 'scope',
        'scope': None,
    }

    def __init__(self, app=None, credentials_store=None):
        # Initialize credentials store
        self.credentials_store = credentials_store or Tools.ttl_cache()

        # Initialize keycloak config
        self.client_secrets = self._set_kc_uris()

        # Initialize Oauth2client
        self.flow = flow_from_clientsecrets(
            "faker_path",
            scope=OIDC_CONFIG['OIDC_SCOPES'],
            cache=DummySecretsCache({TYPE_WEB: self.client_secrets}))

        # Encrypt and decrypt origin_path
        # Encrypt and decrypt origin_path
        self.extra_data_serializer = JSONWebSignatureSerializer(OIDC_CONFIG['SECRET_KEY'])

        # Forced refresh every 1 hour
        self.cookie_serializer = TimedJSONWebSignatureSerializer(
            OIDC_CONFIG['SECRET_KEY'],
            expires_in=OIDC_CONFIG['MAX_EXP']
        )
        self.check_action = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        add
            keycloak callback path & view
            login / logout path & view

        set before_request & after_request
        """
        # keycloak callback
        app.add_url_rule(
            OIDC_CONFIG['CALLBACK_ROUTE'],
            endpoint=OIDC_CONFIG['CALLBACK_ENDPOINT'],
            view_func=self._oidc_callback
        )

        # /login page
        app.add_url_rule(
            OIDC_CONFIG['LOGIN_PATH'],
            endpoint=OIDC_CONFIG['LOGIN_ENDPOINT'],
            view_func=self._login
        )

        # /logout page
        app.add_url_rule(
            OIDC_CONFIG['LOGOUT_PATH'],
            endpoint=OIDC_CONFIG['LOGOUT_ENDPOINT'],
            view_func=self._logout
        )

        app.before_request(self._before_request)
        app.after_request(self._after_request)

    def _oidc_callback(self):
        """view of keycloak callback

        Mainly handles the callback after login keycloak successfully
        and redirect origin path
        :returns: error_response with 401
                    or redirect to the page that the user was going to
        :rtype: response or redirect
        """
        status, data = self._process_callback()
        return data if status else redirect(data)

    def _process_callback(self):
        """Exchange auth code and save credentials
        into credentials_store

        Exchange the auth code for actual credentials,
        then redirect to the originally requested page.
        """
        try:
            state = self._json_loads(
                urlsafe_b64decode(request.args['state'].encode('utf-8'))
            )
            code = request.args['code']
        except (KeyError, ValueError):
            logger.error("Can't retrieve state or auth code "
                         "with request.args: {}".format(request.args),
                         exc_info=True)
            return True, self._oidc_error()

        # loads origin path
        try:
            origin_uri = self.extra_data_serializer.loads(
                state[self.DESTINATION]
            )
        except BadSignature:
            logger.error('State field was invalid')
            return True, self._oidc_error()
        # make a request to keycloak.token_uri to
        # exchange the auth code for OAuth credentials
        flow = self._flow_for_request()
        credentials = flow.step2_exchange(code)

        # check id_token from response of keycloak.token_uri
        id_token = credentials.id_token
        if not self._is_id_token_valid(id_token):
            logger.error("Invalid ID token")
            return True, self._oidc_error()

        # store credentials
        self.save_credentials(credentials, id_token)

        # set a persistent signed cookie containing the ID token
        self._set_cookie_id_token(id_token, changed=True)
        return False, origin_uri

    def _login(self):
        """view of login

        set origin_path and redirect to keycloak auth uri
        :returns:
        :rtype:
        """
        home_uri = urljoin(
            "{scheme}://{netloc}".format(
                scheme=urlparse(request.url).scheme,
                netloc=urlparse(request.url).netloc
            ),
            OIDC_CONFIG['HOME_PAGE']
        )
        # home_uri = "http://172.16.10.212:8000/"
        auth_uri = self.redirect_to_auth_server(home_uri)

        return redirect(auth_uri)

    def redirect_to_auth_server(self, origin_path):
        """Set origin path in the session, and redirect to the IdP.

        :param origin_path: The page that the user was going to,
        :type origin_path: str
        :return : keycloak auth uri including encrypted origin_path
        :rtype : str
        """
        state = {
            self.DESTINATION:
                self.extra_data_serializer.dumps(origin_path).decode('utf-8')
        }
        extra_params = {
            'state': urlsafe_b64encode(json.dumps(state).encode('utf-8')),
            'openid.realm': self.client_secrets['realm'],
        }
        flow = self._flow_for_request()
        auth_url = '{url}&{extra_params}'.format(
            url=flow.step1_get_authorize_url(),
            extra_params=urlencode(extra_params)
        )
        self._set_cookie_id_token(None)
        return auth_url

    def _logout(self):
        """view of login

        del current credentials from credentials_store
        and request to keycloak to logout current session
        :returns:
        :rtype:
        """
        kc_token = self._get_cookie_id_token()
        credentials = self.get_credentials(kc_token.payload)
        self.remove_credentials(kc_token.payload)
        self._set_cookie_id_token(None, changed=True)
        self._logout_user_session(OAuth2Credentials.from_json(credentials))

        return jsonify()

    def _before_request(self):
        """do something before handler request:

        1 set g.oidc_id_token to None
        2 check oidc_token
        Sets g.oidc_id_token to the oidc_token
        if the user has successfully authenticated,
        else returns a redirect to login page
        so user can go try to authenticate.
        :returns: A redirect object, or None
            if the user is logged in.
        :rtype: Redirect
        """
        self._set_cookie_id_token(None)
        # some pages no need to auth like login...
        if self._pass_auth():
            return None

        # find signed ID token from cookie
        kc_token = self._get_cookie_id_token()

        # redirect login page if oidc_token from cookie is None or Invalid
        result = self.check_token(kc_token, request.url)
        if isinstance(result, bool):
            if not result:
                auth_uri = self.redirect_to_auth_server(request.url)
                return redirect(auth_uri)
        else:
            return result

    def _after_request(self, response):
        """
        Set a new ID token cookie if the ID token has changed.
        """
        cookie_secure = OIDC_CONFIG.get('OIDC_ID_TOKEN_COOKIE_SECURE', True)
        if getattr(g, 'oidc_id_token_dirty', False):
            if g.oidc_id_token:
                slimed_token = self.slim_token(
                    g.oidc_id_token,
                    payload_items=self.BASE_TOKEN_ITEM
                )
                signed_id_token = self.cookie_serializer.dumps(slimed_token)
                response.set_cookie(
                    OIDC_CONFIG['OIDC_ID_TOKEN'],
                    signed_id_token,
                    secure=cookie_secure,
                    httponly=True,
                    max_age=OIDC_CONFIG['COOKIE_TTL'])
            else:
                # logout
                response.set_cookie(
                    OIDC_CONFIG['OIDC_ID_TOKEN'],
                    '',
                    path=OIDC_CONFIG['COOKIE_PATH'],
                    secure=cookie_secure,
                    httponly=True,
                    expires=0)
        return response

    def check_token(self, kc_token, orgin_path, action='cached'):
        """
        check_token_not_None
        check_cache
        check_exp
        check_scope
        """
        if kc_token is None:
            return False

        self.check_action = getattr(self, '_is_%s' % action)
        token_check_result = self.check_action(kc_token)
        if isinstance(token_check_result, bool):
            if token_check_result:
                next_action = self.check_action_mapping.get(action, None)
                return self.check_token(
                    kc_token, orgin_path,
                    action=next_action) if next_action else True
            else:
                return False
        else:
            return token_check_result

    def _is_cached(self, kc_token):
        """
        Check token cached
        """
        cached_credential = self.get_credentials(kc_token.payload)
        if not cached_credential:
            return False
        kc_token.credentials = cached_credential
        kc_token.access_token = OAuth2Credentials.from_json(
            cached_credential).access_token
        return True

    def _is_exp(self, kc_token):
        """Check token exp

        refresh token or extend exp
        """
        if time.time() < kc_token.payload['exp']:  # keycloak 默认 5min
            return True
        else:
            # oidc_token expired ==> refresh or extend exp
            try:
                # get credentials from cache
                credentials = OAuth2Credentials.from_json(
                    self.get_credentials(kc_token.payload)
                )
            except KeyError:
                # redirect login page if no current oidc_token cache
                logger.debug("Expired ID token, credentials missing",
                             exc_info=True)
                return False

            # refresh and store credentials
            try:
                credentials.refresh(httplib2.Http())  # refresh
                if credentials.id_token:
                    kc_token.payload = credentials.id_token
                else:
                    # It is not guaranteed that we will
                    # get a new oidc_token on refresh,
                    # so if we do not, let's just update
                    # the id token expiry field
                    # and reuse the existing oidc_token.
                    if credentials.token_expiry is None:
                        logger.debug('Expired ID token, no new expiry. '
                                     'Falling back to assuming %s seconds'
                                     % str(OIDC_CONFIG['Extended_Expiration']))
                        kc_token.payload['exp'] = time.time() + \
                                                  int(OIDC_CONFIG['Extended_Expiration'])
                    else:
                        kc_token.payload['exp'] = calendar.timegm(
                            credentials.token_expiry.timetuple())
                self.save_credentials(credentials, kc_token.payload)
                self._set_cookie_id_token(kc_token.payload, changed=True)
                return True
            except AccessTokenRefreshError:
                # Can't refresh. Wipe credentials
                # and redirect user to IdP for re-authentication.
                logger.warning("Expired ID token, can't refresh credentials",
                               exc_info=True)
                self.remove_credentials(kc_token.payload)
                return False

    def _is_scope(self, kc_token):
        """
        check cards access
        """
        require_access = request.headers.get(self.REQUIRE_ACCESS)
        if not require_access:
            logger.info('current page no need access')
            return True
        if isinstance(require_access, str):
            require_access = require_access.encode('utf8')
        require_access = base64.b64decode(require_access).decode('utf8')
        user_access = kc_token.payload.get(self.ACCESS, [])

        if require_access.strip() not in user_access:
            logger.warning('current user has no access {}'.format(require_access))
            return {'msg': 'No access with {}'.format(require_access), 'data': {}}, 403

        return True

    @staticmethod
    def _set_kc_uris():
        """set base keycloak config

        :return: keycloak config mapping
        :rtype: dict
        """
        kc = dict()
        kc['issuer'] = urljoin(KC_CONFIG['KC_AUTH_URI'],
                               '/auth/realms/{}'.format(KC_CONFIG['KC_REALMS']))
        kc['auth_uri'] = "/".join([kc['issuer'],
                                   'protocol/openid-connect/auth'])
        kc['userinfo_uri'] = "/".join([kc['issuer'],
                                       'protocol/openid-connect/userinfo'])
        kc['token_uri'] = "/".join([kc['issuer'],
                                    'protocol/openid-connect/token'])
        kc['logout_uri'] = "/".join([kc['issuer'],
                                     'protocol/openid-connect/logout'])
        kc['token_introspection_uri'] = "/".join([kc['token_uri'], 'introspect'])
        kc['client_id'] = KC_CONFIG['KC_CLIENT_ID']
        kc['client_secret'] = KC_CONFIG['KC_CLIENT_SECRET']
        kc['realm'] = KC_CONFIG['KC_REALMS']
        return kc

    @staticmethod
    def _json_loads(content):
        if not isinstance(content, str):
            content = content.decode('utf-8')
        return json.loads(content)

    @staticmethod
    def _oidc_error(message='Not Authorized', code=401):
        return message, code, {'Content-Type': 'text/plain', }

    def _flow_for_request(self):
        """
        Build a flow with the correct absolute
        callback URL for this request.
        :return:
        """
        flow = copy(self.flow)
        flow.redirect_uri = url_for(OIDC_CONFIG['CALLBACK_ENDPOINT'],
                                    _external=True)
        return flow

    def _is_id_token_valid(self, id_token):
        """
        Check if `id_token` is a current ID token for this application,
        was issued by the Apps domain we expected,
        and that the email address has been verified.

        @see: http://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
        """
        # step 1: check empty
        if not id_token:
            return False

        # step 2: check issuer
        if id_token['iss'] not in self.client_secrets.get('issuer'):
            logger.error('id_token issued by non-trusted issuer: %s'
                         % id_token['iss'])
            return False

        if isinstance(id_token['aud'], list):
            # step 3 for audience list
            if self.flow.client_id not in id_token['aud']:
                logger.error('We are not a valid audience')
                return False
            # step 4
            if 'azp' not in id_token:
                logger.error('Multiple audiences and not authorized party')
                return False
        else:
            # step 3 for single audience
            if id_token['aud'] != self.flow.client_id:
                logger.error('We are not the audience')
                return False

        # step 5 AZP checked
        if 'azp' in id_token and id_token['azp'] != self.flow.client_id:
            logger.error('Authorized Party is not us')
            return False

        # step 6: check exp
        if int(time.time()) >= int(id_token['exp']):
            logger.error('Token has expired')
            return False

        # step 7: check iat
        if id_token['iat'] < (time.time() - OIDC_CONFIG['OIDC_CLOCK_SKEW']):
            logger.error('Token issued in the past')
            return False

        # step 8 check email_verified
        if not id_token.get('email_verified', False) and\
                OIDC_CONFIG['OIDC_REQUIRE_VERIFIED_EMAIL']:
            logger.error('Email not verified')
            return False

        return True

    def save_credentials(self, credentials, token):
        token_key = self.compute_token_key(token)
        self.credentials_store.set(token_key, credentials.to_json())

    def compute_token_key(self, token):

        content = '{sub}_{session_state}_{jti}'.format(
            sub=token['sub'],
            session_state=token['session_state'],
            jti=token['jti']
        )
        token_key = Tools.compute_md5(content)
        return token_key

    def _set_cookie_id_token(self, id_token, changed=False):
        """Save id_token with g

        save current token in g.oidc_id_token
        and add a flag to record if it has changed for
        cooperates with @after_request to
        set a new id_token to cookie.
        """
        g.oidc_id_token = id_token
        g.oidc_id_token_dirty = changed

    def _logout_user_session(self, credentials):
        """
        Request to keycloak for logout current session
        """
        body = {
            'client_id': self.client_secrets['client_id'],
            'client_secret': self.client_secrets['client_secret'],
            'refresh_token': credentials.refresh_token
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer {}'.format(credentials.access_token)
        }
        resp, _ = httplib2.Http().request(
            self.client_secrets['logout_uri'],
            "POST",
            body=urlencode(body),
            headers=headers)
        if resp.status != 204:
            raise Exception('Logout current user fail')

    def _pass_auth(self):
        """
        Collection of endpoint that do not require authentication
        """
        return request.endpoint in frozenset(
            [
                OIDC_CONFIG['CALLBACK_ENDPOINT'],
                OIDC_CONFIG['CALLBACK_ERROR_ENDPOINT'],
                OIDC_CONFIG['LOGIN_ENDPOINT'],
                OIDC_CONFIG['LOGOUT_ENDPOINT'],
            ]
        )

    def _get_cookie_id_token(self):
        """Get oidc_token from cookie and loads

        self.cookie_serializer.loads will check exp in header
        and raise SignatureExpired if it expire
        """
        token_info = None
        cookie_token = request.cookies.get(OIDC_CONFIG['OIDC_ID_TOKEN'])
        if cookie_token:
            try:
                token_info = self.cookie_serializer.loads(cookie_token)
            except SignatureExpired:
                logger.warning("ID token cookie Signature expired",
                               exc_info=True)
                token_info = None
            except Exception:
                logger.error("Can not loads "
                             "oidc_id_token :{}".format(cookie_token),
                             exc_info=True)
                logger.error(traceback.format_exc())

        if token_info:
            return KCToken(payload=token_info, cookies_token=cookie_token)
        return None

    def get_credentials(self, token):
        """
        Find current user credentials from cache
        """
        token_key = self.compute_token_key(token)
        return self.credentials_store.get(token_key)

    def remove_credentials(self, token):
        """
        Clear current user token when logout
        """
        token_key = self.compute_token_key(token)
        if self.credentials_store.get(token_key):
            self.credentials_store.delete(token_key)

    def slim_token(self, id_token, payload_items=None):
        """Just return necessary info in cookie

        :return: payload
        :rtype: dict
        """
        return {key: id_token[key] for key in payload_items if key in id_token} \
            if payload_items else id_token
