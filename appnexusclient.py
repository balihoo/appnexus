import requests
from requests.compat import urljoin, quote_plus
import memcache
import contextlib
from time import time
import json
import logging

import config

class AuthException(Exception):
    pass

class AppNexusClient(object):
    AUTH_TIMEOUT_SEC = 7200 #times out every 2h (7200 sec)
    TEST_URI = "http://api-test.appnexus.com"
    PROD_URI = "http://api.appnexus.com"
    CONTENT_HDR = {'Content-type': 'application/json; charset=UTF-8'}

    def __init__(self, token=None, refresh_from_memcache=False):
        self._token = token
        self._token_ts = time() if token else 0
        self.uri = self.PROD_URI if config.env == "prod" else self.TEST_URI
        self.refresh_from_memcache = refresh_from_memcache
        if refresh_from_memcache:
            self.mcache = memcache.Client([config.memcache_host, config.memcache_port])

    def token(self):
        #preemtively reauth at 80% of expiration time
        if time() - self._token_ts > (0.8 * self.AUTH_TIMEOUT_SEC):
            logging.info("re-auth due to time")
            self._refresh_token()
        return self._token

    def apiuri(self, term):
        return urljoin(self.uri, quote_plus(term))

    def apihdr(self, hdr=None):
        headers = hdr or {}
        headers.update(self.CONTENT_HDR)
        headers.update({'Authorization': self.token()})
        return headers

    def _refresh_token(self):
        if self.refresh_from_memcache:
            key="appnexus{}".format(config.env),
            token = memcache.get(key)
            if not token:
                raise AuthException("Unable to get token from cache with {}".format(key))
            self.token = token
        else:
            data = json.dumps({'auth': {'username':config.username, 'password':config.password}})
            uri = self.apiuri('auth')
            res = requests.post(uri, data=data, headers=self.CONTENT_HDR).json()['response']
            if res.get('status') == "OK":
                self._token = res['token']
                self._token_ts = time()
                logging.info("new token: [{}] @ {}".format(self._token, self._token_ts))
            else:
                raise AuthException("Unable to refresh token: {}".format(json.dumps(res, indent=4)))

    def _ensure_auth(self, reqf):
        res = reqf()
        if res.get('error_id') == "NOAUTH":
            logging.info("re-auth due to noauth")
            self._refresh_token()
            res = reqf()
        return res

    def _get(self, what, headers=None):
        uri = self.apiuri(what)
        headers = self.apihdr(headers)
        reqf = lambda: requests.get(uri, headers=headers).json()['response']
        return self._ensure_auth(reqf)

