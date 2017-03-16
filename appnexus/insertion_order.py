from itertools import chain
from .sub_service import SubService
from .line_item import LineItem
from .paginator import paginator

class InsertionOrder(SubService):
    service_name = 'insertion-order'
    collection_name = 'insertion-orders'

    def __init__(self,  *args, **kwargs):
        super(InsertionOrder, self).__init__(*args, **kwargs)
        self._line_items = []

    def _new_line_items(self):
        return [li for li in self._line_items if li.id is None]


    def create_line_item(self, name, **kwargs):
        """ create a new line_item """
        data = { 'name': name, 'advertiser_id': self.advertiser_id, 'insertion_orders': [ { 'id': self.id }] }
        data.update(kwargs)
        line_item = LineItem(self._client, data=data)
        self._line_items.append(line_item)
        return line_item

    def line_items(self):
        """ return all line_items """
        line_item_refs = self.data.get('line_items') or []
        remote_line_items = self.line_items_by_ids(li['id'] for li in line_item_refs)
        return chain(remote_line_items, self._new_line_items())

    def line_item_by_name(self, name):
        """ return the first line_item with this name, or None if not found """
        return self._by_inexact_key(LineItem, 'name', name)

    def line_item_by_code(self, line_item_code):
        """ return the line_item with this code, or None if not found """
        return self._by_exact_key(LineItem, 'code', line_item_code)

    def line_item_by_id(self, line_item_id):
        """ return the line_item with this id, or None if not found """
        return self._by_exact_key(LineItem, 'id', line_item_id)

    def line_items_by_ids(self, line_item_ids):
        """ return an iterator for line items with these ids """
        return self._by_ids(LineItem, line_item_ids)


    def save(self):
        """ creates or updates the item remotely """
        advid = self.advertiser_id
        existing_line_items = self.data.get('line_items', []) or []
        for li in self._new_line_items():
            li.save()
            li_summary = {k:li.data.get(k) for k in ('id', 'name', 'code', 'state', 'start_date', 'end_date', 'timezone')}
            existing_line_items.append(li_summary)
        self.data['line_items'] = existing_line_items

        payload = { self.service_name: self.data }
        if self.data.get('id') is None:
            #new
            res = self._client.post('{}?advertiser_id={}'.format(self.service_name, advid), payload)
        else:
            #update
            res = self._client.put('{}?id={}&advertiser_id={}'.format(self.service_name, self.data['id'], advid), payload)
        self.data.update(res[self.service_name])
        return True

