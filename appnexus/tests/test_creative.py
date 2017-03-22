from unittest import TestCase
import json

from mock_client import MockAppNexusClient
from appnexus import resource

class MyMockClient(MockAppNexusClient):
    def handler(self, method, service, params, data, headers):
        if False:
            print("method: {}".format(method))
            print("service: {}".format(service))
            print("params: {}".format(params))
            print("data: {}".format(data))
            print("headers: {}".format(headers))
        return {
            'advertiser': { 'id': 1 },
            'insertion-order': { 'id': 1, 'advertiser_id': 1, 'name': 'imanio' },
            'line-item': { 'id': 1, 'advertiser_id': 1, 'insertion_order_id': 1, 'name': 'imanli', 'campaigns': [{'id':1}] },
            'campaign': { 'id': 1, 'advertiser_id': 1, 'insertion_order_id': 1, 'line-item_id': 1, 'name': 'imacampaign', 'creatives': [ {'id':1, 'code':1}] },
            'media-asset': [ { 'id': 1 } ],
            'creative-html': { 'id': 1, 'advertiser_id':1, 'code':1 },
        }

def mock_resource():
    cfg = {}
    res = resource.AppNexusResource(cfg)
    res._client = MyMockClient(cfg)
    return res

class TestCreative(TestCase):
    def test_handler(self):
        res = mock_resource()
        adv = res.advertiser_by_id(1)
        io = adv.insertion_order_by_id(1)
        li = io.line_item_by_id(1)
        cp = li.campaign_by_id(1)
        crea = cp.creative_by_code(1)
        crea.data['name'] = 'crea'
        crea.data['code'] = 1
        crea.data['brand_id'] = 1
        crea.data['width'] = 1
        crea.data['height'] = 1
        crea.save()
        self.assertEqual(crea.id, 1)
