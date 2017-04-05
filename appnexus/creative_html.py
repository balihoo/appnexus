from .sub_service import SubService
class CreativeHtml(SubService):
    service_name = 'creative-html'
    collection_name = 'creatives'

    def deactivate(self):
        """ sets the creative state to inactive """
        if self.data.get('id'):
            payload = {
                self.service_name: {
                    'state': 'inactive',
                    'status': {
                        'user_ready': False
                    }
                }
            }
            res = self._client.put('{service_name}?id={id}&advertiser_id={advertiser_id}'.format(
                service_name=self.service_name,
                id=self.data['id'],
                advertiser_id=self.data['advertiser_id'],
            ), payload)
            self.data.update(res[self.service_name])

        return True