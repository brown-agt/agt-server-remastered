from abc import ABC, abstractmethod
from typing import Set, List, Dict
import itertools
from agt_server.agents.utils.adx.structures import Campaign
from agt_server.agents.base_agents.adx_agent import NDaysNCampaignsAgent



class State(ABC):
    _uid_generator = itertools.count(1)

    uid: int

    def __init__(self):
        super().__init__()
        self.uid = next(type(self)._uid_generator)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.uid == other.uid

    def __hash__(self):
        return hash(self.__class__.__name__ + str(self.uid))

    @abstractmethod
    def to_vector(self):
        return [self.uid]


class BidderState(State):
    _uid_generator = itertools.count(1)

    bidder: NDaysNCampaignsAgent

    def __init__(self, bidder):
        super().__init__()
        self.bidder = bidder

    def to_vector(self):
        return super().to_vector()


class CampaignBidderState(BidderState):
    _uid_generator = itertools.count(1)

    campaigns: Set[Campaign]
    budgets: Dict[Campaign, float]
    spend: Dict[Campaign, float]  # How much has been spent so far on each campaign (e.g., via bids won)
    impressions: Dict[Campaign, int]  # How many impressions have been acquired for each campaign
    quality_score: float
    timestep: int  # e.g., day of the AdX game

    def __init__(self, bidder, campaign: Campaign = None, budget: float = 0.0, spend: float = 0.0, impressions: int = 0, timestep: int = 0):
        super().__init__(bidder)
        self.campaigns = {campaign.uid: campaign} if campaign else {}
        self.budgets = {campaign.uid: budget} if campaign else {}
        self.spend = {campaign.uid: spend} if campaign else {}
        self.impressions = {campaign.uid: impressions} if campaign else {}
        self.expenditure = 0
        self.timestep = timestep
        self.profits = 0.0
        self.quality_score = 1.0

    def add_campaign(self, campaign):
        self.campaigns[campaign.uid] = campaign
        self.budgets[campaign.uid] = campaign.budget 
        self.spend[campaign.uid] = 0 
        self.impressions[campaign.uid] = 0 
    
    def add_all(self, campaigns):
        for c in campaigns:
            self.add_campaign(c)

    def __repr__(self):
        return "{}(campaigns: {}, budgets: {}, spend: {}, impressions: {}, timestep: {})".format(
            self.__class__.__name__,
            self.campaigns, self.budgets,
            self.spend, self.impressions,
            self.timestep
        )

    def to_vector(self):
        camp_vecs = []
        for campaign in self.campaigns:
            camp_vec = [campaign.reach, self.budgets[campaign], campaign.target.uid, self.spend[campaign], self.impressions[campaign]]
            camp_vecs.append(camp_vec)
        vec = [len(self.campaigns)] + [item for sublist in camp_vecs for item in sublist] + [self.timestep]
        return vec