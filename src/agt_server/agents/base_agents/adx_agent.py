from typing import Set, List, Dict, Iterable, Callable
import itertools
from abc import ABC, abstractmethod
from agt_server.agents.utils.adx.structures import Campaign, Bid
from math import isfinite, atan

class NDaysNCampaignsAgent(ABC):
    _uid_generator = itertools.count(1)

    uid: int
    def __init__(self):
        self.current_game = 0
        self.init()
        self.uid = next(type(self)._uid_generator)
        
    def init(self):
        self.current_day = 0
        self.quality_score = 1.0
        self.my_campaigns = set()
        self.statistics = {}
        self.profit = 0.0

    def __hash__(self):
        return hash(self.__class__.__name__ + str(self.uid))
    
    def get_quality_score(self) -> float:
        return self.quality_score

    def get_current_day(self) -> int:
        return self.current_day

    def current_game(self) -> int:
        return self.current_game

    def get_active_campaigns(self) -> Set[Campaign]:
        filtered = [c for c in self.my_campaigns if self.current_day >= c.start_day  and self.current_day <= c.end_day]
        return set(filtered)

    def get_cumulative_reach(self, campaign: Campaign) -> int:
        return campaign.cumulative_reach

    def get_cumulative_cost(self, campaign: Campaign) -> float:
         return campaign.cumulative_cost

    def get_cumulative_profit(self) -> float:
        return self.profit

    @staticmethod
    def effective_reach(x: int, R: int) -> float:
        return (2.0 / 4.08577) * (atan(4.08577 * ((x + 0.0) / R) - 3.08577) - atan(-3.08577))

    @staticmethod
    def is_valid_campaign_bid(campaign: Campaign, bid: float) -> bool:
        return isfinite(bid) and 0.1 * campaign.reach <= bid <= campaign.reach

    @staticmethod
    def clip_campaign_bid(campaign: Campaign, bid: float) -> float:
        return max(0.1 * campaign.reach, min(campaign.reach, bid))

    def effective_campaign_bid(self, bid: float) -> float:
        return bid / self.get_quality_score()

    @abstractmethod
    def get_ad_bids(self) -> Set[Bid]:
        pass

    @abstractmethod
    def get_campaign_bids(self, campaigns_for_auction: Set[Campaign]) -> Dict[Campaign, float]:
        pass

    @abstractmethod
    def on_new_game(self):
        pass

    def update_statistics(self, statistics):
        self.statistics.update(statistics)
    
    def __repr__(self):
        return self.name
