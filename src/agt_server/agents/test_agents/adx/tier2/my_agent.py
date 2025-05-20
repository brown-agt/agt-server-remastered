import random
from typing import Set, Dict
from agt_server.agents.utils.adx.structures import Bid, Campaign, BidBundle, MarketSegment
from agt_server.agents.base_agents.adx_agent import NDaysNCampaignsAgent

class Tier2NDaysNCampaignsAgent(NDaysNCampaignsAgent):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def get_ad_bids(self) -> Set[BidBundle]:
        bundles = set()
        for campaign in self.get_active_campaigns():
            bids = set()

            remaining_reach = max(1.0, campaign.reach - self.get_cumulative_reach(campaign))
            remaining_budget = max(1.0, campaign.budget - self.get_cumulative_cost(campaign))

            # Conservative bidding: don't overbid per item
            bid_per_item = min(0.8, remaining_budget / remaining_reach)
            bid_per_item = max(0.05, bid_per_item)

            bid = Bid(
                bidder=self,
                auction_item=campaign.target_segment,
                bid_per_item=bid_per_item,
                bid_limit=remaining_budget
            )
            bids.add(bid)
            bundle = BidBundle(campaign_id=campaign.uid, limit=remaining_budget, bid_entries=bids)
            bundles.add(bundle)
        return bundles

    def get_campaign_bids(self, campaigns_for_auction: Set[Campaign]) -> Dict[Campaign, float]:
        bids = {}
        for campaign in campaigns_for_auction:
            duration = campaign.end_day - campaign.start_day + 1
            # Slightly smarter: prefer shorter campaigns with high reach
            bid_value = campaign.reach / duration
            bids[campaign] = bid_value
        return bids

    def on_new_game(self):
        pass

################### SUBMISSION #####################
my_agent_submission = Tier2NDaysNCampaignsAgent("TA - Tier 2 Agent")
####################################################