from .service import Service
class SubService(Service):
    """ An AppNexus API service that requires an advertiser
    The subclass should set _service_name to the name of the AppNexus API service """
    _service_name = None
    def __init__(self, client, advertiser, data):
        if not self._service_name:
            raise NotImplemented("Service should be subclassed.")
        self._client = client
        self._advertiser = advertiser
        self.data = data

    @property
    def advertiser(self):
        return self.advertiser

    def save(self):
        """ creates or updates the item remotely """
        advid = self.advertiser.id
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
        advid = self.advertiser.id
        if not self.data.get('id') is None:
            res = self._client.delete('{}?id={}&advertiser_id={}'.format(self.service_name, self.data['id'], advid))
            self.data['id'] = None
        else:
            raise DataException("unable to delete {} without an id".format(self.service_name))


