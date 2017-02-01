import json
class Advertiser(object):
    def __init__(self, client, data):
        self._client = client
        self.data = data

    def save(self):
        """ creates or updates the advertiser remotely """
        payload = { 'advertiser': self.data }
        if self.data.get('id') is None:
            #new
            res = self._client.post('advertiser', payload)
            self.data['id'] = res['id']
        else:
            #update
            self._client.put('advertiser?id={}'.format(self.data['id']), payload)
        return True

    def delete(self):
        """ deletes the advertiser remotely.
        Saving it after this will recreate it with a new id
        """
        if not self.data.get('id') is None:
            res = self._client.delete('advertiser?id={}'.format(self.data['id']))
            print(json.dumps(res, indent=4))
            self.data['id'] = None
        else:
            raise DataException("unable to delete advertiser without an id")


