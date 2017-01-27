import requests
from requests.compat import urljoin, quote_plus
import contextlib
from time import time
import json
import logging
import os

import config

class AuthException(Exception):
    pass

class AppNexusResource(object):
    def __init__(self):
        self._client = AppNexusClient()

    def advertiser_by_id(self, advertiser_id):
        a_id = quote_plus(advertiser_id)
        res = self._client.get('advertiser?id={}'.format(a_id))
        if res["status"] == "OK":
            return Advertiser(client=self._client, data=res["advertiser"])

    def advertisers(self):
        res = self._client.get('advertiser')
        if res["status"] == "OK":
            for adv in res["advertisers"]:
                yield Advertiser(client=self._client, data=adv)
            thusfar = res["start_element"] + res["num_elements"]
            while res["count"] > thusfar:
                res = self._client.get('advertiser?start_element={}'.format(thusfar))
                if res["status"] != "OK":
                    return
                for adv in res["advertisers"]:
                    yield Advertiser(client=self._client, data=adv)
                thusfar = res["start_element"] + res["num_elements"]

class Advertiser(object):
    def __init__(self, client, data):
        self._client = client
        self.data = data

class AppNexusClient(object):
    AUTH_TIMEOUT_SEC = 7200 #times out every 2h (7200 sec)
    TEST_URI = "http://api-test.appnexus.com"
    PROD_URI = "http://api.appnexus.com"
    CONTENT_HDR = {'Content-type': 'application/json; charset=UTF-8'}

    def __init__(self):
        """ Basic low level wrapper for the app nexus REST API """
        self.uri = self.PROD_URI if config.env == "prod" else self.TEST_URI
        self._token = None
        self._token_ts = 0
        self._token_file = None
        self.refresh_from_memcache = False
        #check if we have a filesystem stored token
        if hasattr(config, 'token_file'):
            self._token_file = config.token_file
            if os.path.exists(self._token_file):
                self._token_ts = os.path.getmtime(self._token_file)
                with open(self._token_file) as f:
                    self._token = f.read()
        #check if we have a memcache stored token
        elif hasattr(config, 'memcache_host'):
            self.refresh_from_memcache = True
            import memcache
            self.mcache = memcache.Client([config.memcache_host, config.memcache_port])

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
            key="appnexus{}".format(config.env),
            token = memcache.get(key)
            if not token:
                raise AuthException("Unable to get token from cache with {}".format(key))
            self.token = token
        else:
            data = json.dumps({'auth': {'username':config.username, 'password':config.password}})
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

    def _ensure_auth(self, reqf):
        """ attempt an api request and retry with a fresh token if auth fails """
        res = reqf()
        if res.get('error_id') == "NOAUTH":
            logging.info("re-auth due to noauth")
            self._refresh_token()
            res = reqf()
        return res

    def get(self, what, headers=None):
        """ basic api get request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        logging.info("GET {}".format(uri))
        reqf = lambda: requests.get(uri, headers=headers).json()['response']
        return self._ensure_auth(reqf)

    def post(self, what, data, headers=None):
        """ basic api post request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        data = json.dumps(data)
        logging.info("POST {}: {}".format(uri, data))
        reqf = lambda: requests.post(uri, data=data, headers=headers).json()['response']
        return self._ensure_auth(reqf)

    def put(self, what, data, headers=None):
        """ basic api put request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        data = json.dumps(data)
        logging.info("PUT {}: {}".format(uri, data))
        reqf = lambda: requests.put(uri, data=data, headers=headers).json()['response']
        return self._ensure_auth(reqf)

    def delete(self, what, headers=None):
        """ basic api delete request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        logging.info("DELETE {}".format(uri))
        reqf = lambda: requests.delete(uri, headers=headers).json()['response']
        return self._ensure_auth(reqf)
