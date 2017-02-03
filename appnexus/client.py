import requests
from requests.compat import urljoin
import contextlib
import logging
from time import time
import json
import os

from .exceptions import (
    DataException,
    AuthException,
    ApiException,
    NotFoundException
)

class AppNexusClient(object):
    AUTH_TIMEOUT_SEC = 7200 #times out every 2h (7200 sec)
    TEST_URI = "http://api-test.appnexus.com"
    PROD_URI = "http://api.appnexus.com"
    CONTENT_HDR = {'Content-type': 'application/json; charset=UTF-8'}

    def __init__(self, config):
        """ Basic low level wrapper for the app nexus REST API """
        self._config = config
        self.env = self._config.get('env')
        self.uri = self.PROD_URI if self.env  == "prod" else self.TEST_URI
        self._token = None
        self._token_ts = 0
        self.refresh_from_memcache = False
        self._token_file = self._config.get('token_file')
        self._memcache_host = self._config.get('memcache_host')
        self._memcache_port = self._config.get('memcache_port')
        #check if we have a filesystem stored token
        if self._token_file and os.path.exists(self._token_file):
            self._token_ts = os.path.getmtime(self._token_file)
            with open(self._token_file) as f:
                self._token = f.read().strip()
        #check if we have a memcache stored token
        elif self._memcache_host and self._memcache_port:
            self.refresh_from_memcache = True
            import memcache
            self.mcache = memcache.Client([self._memcache_host, self._memcache_port])

    def __error_checked(reqf):
        """ decorator to check for AUTH, HTTP or API error response. """
        tried = False
        def checked_reqf(self, *args, **kwargs):
            r = reqf(self, *args, **kwargs)
            res = r.json().get('response', {})
            if res.get('status') == "OK":
                return res
            if res.get('error_id') == "NOAUTH":
                if not tried:
                    self._refresh_token()
                    return checked_reqf()
                logging.error("AUTH FAILED TWICE")
            r.raise_for_status()
            errid = res.get('error_id')
            error = res.get('error')
            errdesc = res.get('error_description')
            if errid == "SYNTAX" and error == "resource not found":
                raise NotFoundException(r.url)
            raise ApiException("{}: {} {} ({})".format(errid, error, errdesc, r.url))
        return checked_reqf

    def token(self):
        """ get a valid auth token to use in api calls """
        #preemtively reauth at 80% of expiration time
        if time() - self._token_ts > (0.8 * self.AUTH_TIMEOUT_SEC):
            logging.info("re-auth due to time")
            self._refresh_token()
        return self._token

    def _apiuri(self, term):
        """ prepend the base uri to a term """
        return urljoin(self.uri, term)

    def _apihdr(self, hdr=None):
        """ add auth and content type to any custom headers """
        headers = hdr.copy() if hdr else {}
        headers.update(self.CONTENT_HDR)
        headers.update({'Authorization': self.token()})
        return headers

    def _refresh_token(self):
        """ gets a token from memcache, if so configured, or goes out to get it from
        the appnexus auth api. Note that we do NOT attempt to store the token in memcache
        here; the whole point of memcache is to avoid concurrent auth calls: if memcache is
        used, there ought to be a separate process to populate it
        """
        if self.refresh_from_memcache:
            key="appnexus{}".format(self.env)
            token = self.mcache.get(key)
            if not token:
                raise AuthException("Unable to get token from cache with {}".format(key))
            self.token = token
        else:
            u = self._config.get('username')
            p = self._config.get('password')
            if not u and p:
                raise AuthException("username and/or password not set in config")
            data = json.dumps({'auth': { 'username': u, 'password': p }})
            uri = self._apiuri('auth')
            res = requests.post(uri, data=data, headers=self.CONTENT_HDR).json()['response']
            if res.get('status') == "OK":
                self._token = res['token']
                self._token_ts = time()
                logging.info("new token: [{}] @ {}".format(self._token, self._token_ts))
                if self._token_file:
                    with open(self._token_file, 'w') as f:
                        f.write(self._token)
            else:
                raise AuthException("Unable to refresh token: {}".format(json.dumps(res, indent=4)))

    @__error_checked
    def get(self, what, headers=None):
        """ basic api get request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        logging.info("GET {}".format(uri))
        return requests.get(uri, headers=headers)

    @__error_checked
    def post(self, what, data, headers=None):
        """ basic api post request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        data = json.dumps(data)
        logging.info("POST {}: {}".format(uri, data))
        return requests.post(uri, data=data, headers=headers)

    @__error_checked
    def put(self, what, data, headers=None):
        """ basic api put request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        data = json.dumps(data)
        logging.info("PUT {}: {}".format(uri, data))
        return requests.put(uri, data=data, headers=headers)

    @__error_checked
    def delete(self, what, headers=None):
        """ basic api delete request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        logging.info("DELETE {}".format(uri))
        return requests.delete(uri, headers=headers)
