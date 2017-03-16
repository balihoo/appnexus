from time import time

from appnexus.client import AppNexusClient
from requests.exceptions import HttpError

class MockResponse(object):
    def __init__(self, data, code=200):
        self._data = data
        self.code = code

    def raise_for_status(self):
        if self.code != 200:
            raise HttpError("code = {}".format(self.code))

    def json(self):
        if 'status' not in self._data:
            self._data['status'] = "OK"
        return { 'response': self._data }

class MockAppNexusClient(AppNexusClient):
    def __init__(self, config):
        """ Mocked low level wrapper for the app nexus REST API """
        self._config = config
        self.env = self._config.get('env')
        self.uri = self.PROD_URI if self.env  == "prod" else self.TEST_URI
        self._token = None
        self._token_ts = 0
        self.refresh_from_memcache = False
        #override the requests methods
        self._get = self._mk_mock('GET', self.handler)
        self._put = self._mk_mock('PUT', self.handler)
        self._post = self._mk_mock('POST', self.handler)
        self._delete = self._mk_mock('DELETE', self.handler)

    def _refresh_token(self):
        self._token = "MOCKTOKEN"
        self._token_ts = time()

    def _dissect_uri(self, uri):
        """ break apart an AppNexus uri into the service and parameters """
        bare = uri.replace(self.uri, '').strip('/')
        service, param_str = bare.split("?")
        param_pairs = param_str.split('&')
        pairs = [tuple(p.split("=")) for p in param_pairs]
        params = dict(pairs)
        return (service, params)

    def _mk_mock(self, method, handler):
        """ provide a substitute method for requests calls,
        break apart components and return a mock requests response
        object
        """
        def mock_response(uri, data=None, headers=None):
            (service, params) = self._dissect_uri(uri)
            response_data = handler(method, service, params, data, headers)
            return MockResponse(response_data)
        return mock_response

    def handler(self, method, service, params, data, headers):
        """ override this to implement different responses to
        different requests calls
        """
        return { 'id': 0 }

