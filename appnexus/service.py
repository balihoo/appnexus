class Service(object):
    """  The subclass should set _service_name to the name of the AppNexus API service """
    service_name = None
    collection_name = None

    def __init__(self, client, data):
        if not (self.service_name and self.collection_name):
            raise NotImplemented("Service should be subclassed with a service and collection name.")
        self._client = client
        self.data = data

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


