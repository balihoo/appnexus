from advertiser import Advertiser
from client import AppNexusClient
from requests.compat import quote_plus
from .exceptions import NotFoundException

class AppNexusResource(object):
    def __init__(self, config):
        self._client = AppNexusClient(config)

    def _paginator(self, term, collection_name, cls):
        """ returns a generator that fetches elements as needed """
        res = self._client.get(term)
        if res["status"] == "OK":
            for item in res[collection_name]:
                yield cls(client=self._client, data=item)
            thusfar = res["start_element"] + res["num_elements"]
            separator = '&' if '?' in term else '?'
            while res["count"] > thusfar:
                res = self._client.get('{}{}start_element={}'.format(term, separator, thusfar))
                for item in res[collection_name]:
                    yield cls(client=self._client, data=item)
                thusfar = res["start_element"] + res["num_elements"]

    def create_advertiser(self, name, **kwargs):
        """ create a new advertiser """
        data = { 'name': name }
        data.update(kwargs)
        return Advertiser(self._client, data=data)

    def advertisers(self):
        """ return all advertisers """
        return self._paginator('advertiser', 'advertisers', Advertiser)

    def advertisers_by_ids(self, advertiser_ids):
        """ return multiple advertisers by id """
        term = 'advertiser?id={}'.format(','.join(advertiser_ids))
        return self._paginator(term, 'advertisers', Advertiser)

    def advertiser_by_id(self, advertiser_id):
        """ return a specific advertiser """
        a_id = quote_plus(str(advertiser_id))
        try:
            res = self._client.get('advertiser?id={}'.format(a_id))
            return Advertiser(client=self._client, data=res["advertiser"])
        except NotFoundException:
            return None

    def advertiser_by_name(self, name):
        """ return the first advertiser with this exact name"""
        term = 'advertiser?name={}'.format(quote_plus(name))
        it = self._paginator(term, 'advertisers', Advertiser)
        return next(it, None)


