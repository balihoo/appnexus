from .service import Service
from .insertion_order import InsertionOrder
from .profile import Profile
from .paginator import paginator

class Advertiser(Service):
    service_name = 'advertiser'
    collection_name = 'advertisers'

    def create_insertion_order(self, name, **kwargs):
        """ create a new insertion_order """
        data = { 'name': name, 'advertiser_id': self.id }
        data.update(kwargs)
        return InsertionOrder(self._client, data=data)

    def insertion_orders(self):
        """ return all insertion_orders """
        return self._all(InsertionOrder)

    def insertion_order_by_name(self, name):
        """ return the first insertion_order with this name, or None if not found """
        return self._by_inexact_key(InsertionOrder, 'name', name)

    def insertion_order_by_code(self, insertion_order_code):
        """ return the insertion_order with this code, or None if not found """
        return self._by_exact_key(InsertionOrder, 'code', insertion_order_code)

    def insertion_order_by_id(self, insertion_order_id):
        """ return the insertion_order with this id, or None if not found """
        return self._by_exact_key(InsertionOrder, 'id', insertion_order_id)

    def insertion_orders_by_ids(self, insertion_order_ids):
        """ return an iterator for insertion_orders with these ids """
        return self._by_ids(InsertionOrder, insertion_order_ids)


