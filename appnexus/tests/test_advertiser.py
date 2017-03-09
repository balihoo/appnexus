from unittest import TestCase

from mock_client import MockAppNexusClient
from appnexus import resource

class MyMockClient(MockAppNexusClient):
    def handler(self, method, service, params, data, headers):
        print("method: {}".format(method))
        print("service: {}".format(service))
        print("params: {}".format(params))
        print("data: {}".format(data))
        print("headers: {}".format(headers))
        return { 'advertiser': { 'id': 0 } }

def mock_resource():
    cfg = {}
    res = resource.AppNexusResource(cfg)
    res._client = MyMockClient(cfg)
    return res

class TestAdvertiser(TestCase):
    def test_get_advertiser(self):
        res = mock_resource()
        adv = res.advertiser_by_id(0)
        self.assertEqual(adv.id, 0)
