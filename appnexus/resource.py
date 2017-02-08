from requests.compat import quote_plus
from .exceptions import NotFoundException
from .advertiser import Advertiser
from .client import AppNexusClient
from .paginator import paginator

class AppNexusResource(object):
    def __init__(self, config):
        self._client = AppNexusClient(config)

    def _all(service):
        """ return all hosted items of a service """
        return paginator(service.service_name, service.collection_name, service)

    def _by_ids(self, service, ids):
        """ return multiple items by id """
        term = '{}?id={}'.format(service.service_name, ','.join(advertiser_ids))
        return paginator(term, service.collection_name, service)

    def _by_exact_key(self, service, key_name, key_value):
        """ return a specific item by an exact key (generally code or id) """
        try:
            res = self._client.get('{}?{}={}'.format(service.service_name, quote_plus(str(key_name)), key_value))
            return Advertiser(client=self._client, data=res[service.service_name])
        except NotFoundException:
            return None

    def _by_inexact_key(self, service, key_name, key_value):
        """ return the first item with this key/value """
        term = '{}?{}={}'.format(service.service_name, quote_plus(str(key_name)), key_value))
        it = paginator(term, Advertiser.collection_name, Advertiser)
        return next(it, None)

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
        return self._by_inexact_key(self, Advertiser, 'name', name)

    def advertiser_by_code(self, advertiser_code):
        """ return the advertiser with this code, or None if not found """
        return self._by_exact_key(self, Advertiser, 'code', advertiser_code)

    def advertiser_by_id(self, advertiser_id):
        """ return the advertiser with this id, or None if not found """
        return self._by_exact_key(self, Advertiser, 'id', advertiser_id)

    def advertisers_by_ids(self, advertiser_ids):
        """ return an iterator for advertisers with these ids """
        return self._by_ids(self, Advertiser, advertiser_ids)

