from .service import Service
from .insertion_order import InsertionOrder
from .paginator import paginator

class Advertiser(Service):
    service_name = 'advertiser'
    collection_name = 'advertisers'

    def insertion_orders(self):
        term = '{}?advertiser_id={}'.format(InsertionOrder.service_name, self.id)
        return paginator(term, InsertionOrder.collection_name, Advertiser)
