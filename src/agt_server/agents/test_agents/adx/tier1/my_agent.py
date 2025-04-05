import random
from typing import Set, Dict
from agt_server.agents.utils.adx.structures import Bid, Campaign, BidBundle, MarketSegment
from agt_server.agents.base_agents.adx_agent import NDaysNCampaignsAgent

class Tier1NDaysNCampaignsAgent(NDaysNCampaignsAgent):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def get_ad_bids(self) -> Set[BidBundle]:
        bundles = set()
        for campaign in self.get_active_campaigns():
            bids = set()
            bid_per_item = min(1, max(0.1, (campaign.budget - self.get_cumulative_cost(campaign)) /
                               (campaign.reach - self.get_cumulative_reach(campaign) + 0.0001)))
            total_limit = max(1.0, campaign.budget - self.get_cumulative_cost(campaign))
            auction_item = campaign.target_segment
            bid = Bid(self, auction_item, bid_per_item, total_limit)
            bids.add(bid)
            bundle = BidBundle(campaign_id=campaign.uid, limit=total_limit, bid_entries=bids)
            bundles.add(bundle)
        return bundles

    def get_campaign_bids(self, campaigns_for_auction: Set[Campaign]) -> Dict[Campaign, float]:
        bids = {}
        for campaign in campaigns_for_auction:
            bid_value = campaign.reach * (random.random() * 0.9 + 0.1)
            bids[campaign] = bid_value
        return bids

    def on_new_game(self):
        pass

################### SUBMISSION #####################
my_agent_submission = Tier1NDaysNCampaignsAgent("TA - Tier 1 Agent")
####################################################