from requests.compat import quote_plus
from .paginator import paginator
from .exceptions import NotFoundException

class Service(object):
    """  The subclass should set _service_name to the name of the AppNexus API service """
    service_name = None
    collection_name = None

    def __init__(self, client, data):
        if not (self.service_name and self.collection_name):
            raise NotImplemented("Service should be subclassed with a service and collection name.")
        self._client = client
        self.data = data

    def _for_this_service(self, term):
        """ add a filter for this service id to the uri term """
        separator = '&' if '?' in term else '?'
        return term + "{}{}_id={}".format(separator, self.service_name, self.id)

    def _all(self, service):
        """ return all hosted items of a service, filtered by this service's id """
        if self.id:
            term = self._for_this_service(service.service_name)
            return paginator(self._client, term, service.collection_name, service)
        return []

    def _by_ids(self, service, ids):
        """ return multiple items by id """
        if self.id:
            values = ','.join(quote_plus(str(i)) for i in ids)
            if values:
                term = '{}?id={}'.format(service.service_name, values)
                term = self._for_this_service(term)
                if ',' in values:
                    return paginator(self._client, term, service.collection_name, service)
                res = self._client.get(term)
                return [service(client=self._client, data=res[service.service_name])]
        return []
        
    def _by_exact_key(self, service, key_name, key_value):
        """ return a specific item by an exact key (generally code or id) """
        try:
            term = '{}?{}={}'.format(service.service_name, quote_plus(str(key_name)), key_value)
            term = self._for_this_service(term)
            res = self._client.get(term)
            return service(client=self._client, data=res[service.service_name])
        except NotFoundException:
            return None

    def _by_inexact_key(self, service, key_name, key_value):
        """ return the first item with this key/value """
        term = '{}?{}={}'.format(service.service_name, quote_plus(str(key_name)), key_value)
        term = self._for_this_service(term)
        it = paginator(self._client, term, service.collection_name, service)
        return next(it, None)

    @property
    def id(self):
        return self.data.get('id')

    @property
    def code(self):
        return self.data.get('code')

    @property
    def name(self):
        return self.data.get('name')

    def meta(self):
        """ retrieve the service's meta information """
        res = self._client.get('{}/meta'.format(self.service_name))
        return res

    def save(self):
        """ creates or updates the item remotely """
        payload = { self.service_name: self.data }
        if self.data.get('id') is None:
            #new
            res = self._client.post(self.service_name, payload)
        else:
            #update
            res = self._client.put('{}?id={}'.format(self.service_name, self.data['id']), payload)
        self.data.update(res[self.service_name])
        return True

    def delete(self):
        """ deletes the item remotely.
        Saving it after this will recreate it with a new id
        """
        if not self.data.get('id') is None:
            res = self._client.delete('{}?id={}'.format(self.service_name, self.data['id']))
            self.data['id'] = None
        else:
            raise DataException("unable to delete {} without an id".format(self.service_name))


