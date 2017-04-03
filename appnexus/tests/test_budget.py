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
        if method == 'POST':
            print(service)
            return { 'advertiser': { 'id': 1 }}
        return {
            'advertiser': { 'id': 1 },
            'line-item': { 'id': 1, 'advertiser_id': 1, 'insertion_order_id': 1, 'name': 'imanli', 'campaigns': [{'id':1}] },

            'insertion-order': {
                'id': 1,
                'advertiser_id': 1,
                'name': 'imanio',
                'budget_intervals': [
                    {
                        'id': 1,
                        'start_date': "2017-03-01 00:00:00",
                        'end_date': "2017-04-01 00:00:00",
                        'timezone': "America/Boise",
                    },
                    {
                        'id': 2,
                        'start_date': "2017-03-02 00:00:00",
                        'end_date': "2017-04-02 00:00:00",
                        'timezone': "America/Boise",
                    },
                ]
            },
        }

def mock_resource():
    cfg = {}
    res = resource.AppNexusResource(cfg)
    res._client = MyMockClient(cfg)
    return res

class TestBudget(TestCase):
    def test_new_li(self):
        res = mock_resource()
        adv = res.advertiser_by_id(1)
        io = adv.insertion_order_by_id(1)
        li = io.create_line_item(name="test")
        #print(json.dumps(li.data['budget_intervals'], indent=4))
        self.assertEqual(len(li.data['budget_intervals']), 2)

    def test_existing_li(self):
        res = mock_resource()
        adv = res.advertiser_by_id(1)
        io = adv.insertion_order_by_id(1)
        li = io.line_item_by_id(1)
        self.assertEqual(li.data.get('budget_intervals'), None)

        io_budget_intervals = io.data.get('budget_intervals', [])
        li.update_budgets(io_budget_intervals)
        self.assertEqual(len(li.data['budget_intervals']), 2)

        #non existing dates
        b = io.budget_by_dates(
            "3017-03-02 00:00:00",
            "3017-04-02 00:00:00",
            "America/Boise"
        )
        self.assertEqual(b, None)

        b = io.budget_by_dates(
            "2017-03-02 00:00:00",
            "2017-04-02 00:00:00",
            "America/Boise"
        )
        self.assertEqual(b['id'], 2)
        this_budget = li.budget_by_parent_id(b['id'])
        this_budget['daily_budget'] = 0.34
        this_budget['enable_pacing'] = True
        #print(json.dumps(li.data['budget_intervals'], indent=4))

        self.assertEqual(li.data['budget_intervals'][1]['daily_budget'], 0.34)

