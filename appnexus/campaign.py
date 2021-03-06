from itertools import chain
from .sub_service import SubService
from .creative_html import CreativeHtml
from .profile import Profile

class Campaign(SubService):
    service_name = 'campaign'
    collection_name = 'campaigns'

    def __init__(self,  *args, **kwargs):
        super(Campaign, self).__init__(*args, **kwargs)
        self._creatives = []
        self._profile = None
        self.old_profiles = []

    def _new_creatives(self):
        return [c for c in self._creatives if c.id is None]

    def creatives(self):
        """ return all creatives """
        creative_refs = self.data.get('creatives') or []
        remote_creatives = self._by_ids(
            CreativeHtml,
            [c['id'] for c in creative_refs],
            override_collection_name='creative-html'
        )
        return chain(remote_creatives, self._new_creatives())

    def creative_by_code(self, creative_code):
        """ return the first creative that matches the code """
        return self._by_exact_key(CreativeHtml, 'code', creative_code)

    def creative_by_id(self, creative_id):
        """ return the first creative that matches the creative_id """
        return next((c for c in self.creatives() if c.id == creative_id), None)

    def profile(self):
        """ return the optionally attached profile """
        if self._profile is None:
            profile_id = self.data.get('profile_id')
            if not profile_id is None:
                self._profile = self._by_exact_key(Profile, 'id', profile_id)
        return self._profile

    def create_creative(self, name, **kwargs):
        """ create a new creative """
        data = { 'name': name, 'advertiser_id': self.advertiser_id }
        data.update(kwargs)
        creative = CreativeHtml(self._client, data=data)
        self._creatives.append(creative)
        return creative

    def create_profile(self, name, **kwargs):
        """ create a new profile, sets this campaigns profile to it """
        data = { 'name': name, 'advertiser_id': self.advertiser_id }
        data.update(kwargs)
        if self._profile:
            self.old_profiles.append(self._profile)
        self._profile = Profile(self._client, data=data)
        return self._profile

    def save(self):
        existing_creatives = self.data.get('creatives', []) or []
        for cr in self._new_creatives():
            cr.save()
            cr_summary = {k:cr.data.get(k) for k in (
                "audit_status", "code", "format", "height", "id", "is_expired",
                "is_prohibited", "is_self_audited", "name", "pop_window_maximize",
                "state", "weight", "width")}
            existing_creatives.append(cr_summary)
        self.data['creatives'] = existing_creatives
        if self._profile:
            self._profile.save()
            self.data['profile_id'] = self._profile.id
        #remove replaced profile(s)
        for p in self.old_profiles:
            p.delete()
        self.old_profiles = []
        super(Campaign, self).save()

    def delete(self):
        super(Campaign, self).delete()
        for c in self.creatives():
            c.delete()
        if self._profile:
            self._profile.delete()
        for p in self.old_profiles:
            p.delete()
 

