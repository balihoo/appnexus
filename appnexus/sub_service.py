from .service import Service
from .exceptions import DataException

class SubService(Service):
    """ An AppNexus API service that requires an advertiser
    The subclass should set _service_name to the name of the AppNexus API service """
    def __init__(self, client, data):
        if not self.service_name:
            raise NotImplemented("Service should be subclassed.")
        if 'advertiser_id' not in data:
            raise DataException("Unable to create {} without advertiser_id")

        self._advertiser_id = data['advertiser_id']
        self._client = client
        self.data = data

    def _for_this_service(self, term):
        """ add a filter for this service id to the uri term """
        separator = '&' if '?' in term else '?'
        return term + "{}{}_id={}&advertiser_id={}".format(separator, self.service_name, self.id, self.advertiser_id)

    @property
    def advertiser_id(self):
        return self._advertiser_id

    def save(self):
        """ creates or updates the item remotely """
        advid = self.advertiser_id
        payload = { self.service_name: self.data }
        if self.data.get('id') is None:
            #new
            res = self._client.post('{}?advertiser_id={}'.format(self.service_name, advid), payload)
        else:
            #update
            res = self._client.put('{}?id={}&advertiser_id={}'.format(self.service_name, self.data['id'], advid), payload)
        self.data.update(res[self.service_name])
        return True

    def delete(self):
        """ deletes the item remotely.
        Saving it after this will recreate it with a new id
        """
        advid = self.advertiser_id
        if not self.data.get('id') is None:
            res = self._client.delete('{}?id={}&advertiser_id={}'.format(self.service_name, self.data['id'], advid))
            self.data['id'] = None
        else:
            raise DataException("unable to delete {} without an id".format(self.service_name))


