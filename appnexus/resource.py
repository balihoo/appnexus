from requests.compat import quote_plus
from .exceptions import NotFoundException
from .client import AppNexusClient
from .paginator import paginator
from .advertiser import Advertiser
from .brand import Brand
from .category import Category

class AppNexusResource(object):
    def __init__(self, config):
        self._client = AppNexusClient(config)

    def _all(self, service):
        """ return all hosted items of a service """
        return paginator(self._client, service.service_name, service.collection_name, service)

    def _by_ids(self, service, ids):
        """ return multiple items by id """
        values = ','.join(quote_plus(str(i)) for i in ids)
        term = '{}?id={}'.format(service.service_name, values)
        if ',' in values:
            return paginator(self._client, term, service.collection_name, service)
        else:
            try:
                res = self._client.get(term)
                return [service(client=self._client, data=res[service.service_name])]
            except NotFoundException:
                return []

    def _by_exact_key(self, service, key_name, key_value):
        """ return a specific item by an exact key (generally code or id) """
        try:
            res = self._client.get('{}?{}={}'.format(service.service_name, quote_plus(str(key_name)), quote_plus(str(key_value))))
            return service(client=self._client, data=res[service.service_name])
        except NotFoundException:
            return None

    def _by_inexact_key(self, service, key_name, key_value):
        """ return the first item with this key/value """
        term = '{}?{}={}'.format(service.service_name, quote_plus(str(key_name)), key_value)
        it = paginator(self._client, term, service.collection_name, service)
        return next(it, None)


    def brands(self):
        """ return all brands.
        without simple=true, this counts all attached creatives, which take a long time
        """
        term = "{}?simple=true".format(Brand.service_name)
        return paginator(self._client, term, Brand.collection_name, Brand)

    def brand_by_id(self, brand_id):
        """ return the brand with this id, or None if not found """
        return self._by_exact_key(Brand, 'id', brand_id)

    def brand_by_name(self, brand_name):
        """ return the brand with this name, or None if not found """
        return self._by_inexact_key(Brand, 'name', brand_name)


    def categories(self):
        """ return all categories """
        return self._all(Category)

    def category_by_id(self, category_id):
        """ return the category with this id, or None if not found """
        return self._by_exact_key(Category, 'id', category_id)

    def category_by_name(self, category_name):
        """ return the category with this name, or None if not found """
        return self._by_inexact_key(Category, 'name', category_name)


    def create_advertiser(self, name, **kwargs):
        """ create a new advertiser """
        data = { 'name': name }
        data.update(kwargs)
        return Advertiser(self._client, data=data)

    def advertisers(self):
        """ return all advertisers """
        return self._all(Advertiser)

    def advertiser_by_name(self, name):
        """ return the first advertiser with this name, or None if not found """
        return self._by_inexact_key(Advertiser, 'name', name)

    def advertiser_by_code(self, advertiser_code):
        """ return the advertiser with this code, or None if not found """
        return self._by_exact_key(Advertiser, 'code', advertiser_code)

    def advertiser_by_id(self, advertiser_id):
        """ return the advertiser with this id, or None if not found """
        return self._by_exact_key(Advertiser, 'id', advertiser_id)

    def advertisers_by_ids(self, advertiser_ids):
        """ return an iterator for advertisers with these ids """
        return self._by_ids(Advertiser, advertiser_ids)

