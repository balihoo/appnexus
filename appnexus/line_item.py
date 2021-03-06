from itertools import chain
from .sub_service import SubService
from .profile import Profile
from .campaign import Campaign

class LineItem(SubService):
    service_name = 'line-item'
    collection_name = 'line-items'

    def __init__(self,  *args, **kwargs):
        super(LineItem, self).__init__(*args, **kwargs)
        self._campaigns = []

    def _new_campaigns(self):
        return [c for c in self._campaigns if c.id is None]

    def budget_by_parent_id(self, budget_id):
        budgets = self.data['budget_intervals']
        return next((b for b in budgets if b['parent_interval_id'] == budget_id), None)
        
    def update_budgets(self, io_budget_intervals):
        """ replace budget intervals with references to parent.
         This will clear any line items specific budgets
        """
        budget_ids = (budget['id'] for budget in io_budget_intervals)
        parent_budget_refs = [ { 'parent_interval_id': budget_id } for budget_id in budget_ids]
        self.data['budget_intervals'] = parent_budget_refs

    def profile(self):
        """ return the optionally attached profile """
        profile_id = self.data.get('profile_id')
        if not profile_id is None:
            return self._by_exact_key(Profile, 'id', profile_id)

    def campaigns(self):
        """ return all campaigns """
        campaign_refs = self.data.get('campaigns') or []
        remote_campaigns = self._by_ids(Campaign, [c['id'] for c in campaign_refs])
        return chain(remote_campaigns, self._new_campaigns())

    def campaign_by_code(self, code):
        """ return the first campaign that matches the code """
        return next((c for c in self.campaigns() if c.code == code), None)

    def campaign_by_id(self, campaign_id):
        """ return the campaign with this id, or None if not found """
        return self._by_exact_key(Campaign, 'id', campaign_id)

    def create_campaign(self, name, **kwargs):
        """ create a new campaign """
        data = { 'name': name, 'advertiser_id': self.advertiser_id, 'line_item_id': self.id }
        data.update(kwargs)
        campaign = Campaign(self._client, data=data)
        self._campaigns.append(campaign)
        return campaign

    def save(self):
        existing_campaigns = self.data.get('campaigns', []) or []
        for ca in self._new_campaigns():
            ca.save()
            ca_summary = {k:ca.data.get(k) for k in (
                "cpm_bid_type", "creative_count", "end_date", "id", "inventory_type",
                "name", "priority", "profile_id", "start_date", "statei"
            )}
            existing_campaigns.append(ca_summary)
        self.data['campaigns'] = existing_campaigns
        super(LineItem, self).save()

    def delete(self):
        super(LineItem, self).delete()
        for c in self.campaigns():
            c.delete()


