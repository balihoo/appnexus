import requests
from requests.compat import urljoin, quote_plus
import config
import contextlib
from time import time
from pprint import pprint
import json

class AppNexusClient(object):
    AUTH_TIMEOUT_SEC = 3600 #times out every 2h or 7200 sec. We reauth every hour
    TEST_URI = "http://api-test.appnexus.com"
    PROD_URI = "http://api.appnexus.com"
    def __init__(self):
        self._token = None
        self._token_ts = 0
        self.uri = self.PROD_URI if config.env == "prod" else self.TEST_URI

    def token(self):
        if time() - self._token_ts > self.AUTH_TIMEOUT_SEC:
            self._refresh_token()
        return self._token

    def apiuri(self, term):
        return urljoin(self.uri, quote_plus(term))

    def _refresh_token(self):
        data = json.dumps({'auth': {'username':config.username, 'password':config.password}})
        headers = {'Content-type': 'application/json; charset=UTF-8'}
        uri = self.apiuri('auth')
        res = requests.post(uri, data=data, headers=headers).json()
        if res.get('status') == "OK":
            self.token == res['token']
            self._token_ts = time()
        else:
            raise Exception("Unable to refresh token: {}".format(json.dumps(res, indent=4)))

    def _get(self, what, headers=None):
        uri = "{}/{}".format(self.uri, what)
        headers = headers or {}
        #headers.update({'Authorization': self.token()})
        print("getting {}".format(uri))
        res = requests.get(uri, headers=headers).json()['response']
        #if res.get('error_id') == "NOAUTH":
        #    self._refresh_token()
        #    headers.update({'Authorization': self.token()})
        #    res = requests.get(uri, headers=headers).json()['response']
        pprint(res)
        return res

if __name__ == "__main__":
   client = AppNexusClient()
   print(client.token())
   client._get('members')
