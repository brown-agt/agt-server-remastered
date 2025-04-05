from typing import Set, List, Dict
import itertools

class MarketSegment(frozenset):
    _all_segments = [] 

    def __new__(cls, iterable):
        return super(MarketSegment, cls).__new__(cls, iterable)
    
    def __init__(self, iterable):
        super().__init__()
        self.name = "_".join(iterable)
        
    @classmethod
    def all_segments(cls):
        return cls._all_segments

MarketSegment._all_segments = [
    MarketSegment(("Male", "Young")),
    MarketSegment(("Male", "Old")),
    MarketSegment(("Male", "LowIncome")),
    MarketSegment(("Male", "HighIncome")),
    MarketSegment(("Female", "Young")),
    MarketSegment(("Female", "Old")),
    MarketSegment(("Female", "LowIncome")),
    MarketSegment(("Female", "HighIncome")),
    MarketSegment(("Young", "LowIncome")),
    MarketSegment(("Young", "HighIncome")),
    MarketSegment(("Old", "LowIncome")),
    MarketSegment(("Old", "HighIncome")),
    MarketSegment(("Male", "Young", "LowIncome")),
    MarketSegment(("Male", "Young", "HighIncome")),
    MarketSegment(("Male", "Old", "LowIncome")),
    MarketSegment(("Male", "Old", "HighIncome")),
    MarketSegment(("Female", "Young", "LowIncome")),
    MarketSegment(("Female", "Young", "HighIncome")),
    MarketSegment(("Female", "Old", "LowIncome")),
    MarketSegment(("Female", "Old", "HighIncome"))
]

class Bid:
    _uid_generator = itertools.count(1)
    
    uid: int
    bidder: any
    auction_item_spec: MarketSegment
    bid_per_item: float
    bid_limit: float # same units as bid_per_item (e.g. dollars)

    def __init__(self, bidder, auction_item: Set[str], 
                       bid_per_item: float = 0.0, bid_limit: float = 0.0):
        self.uid = next(type(self)._uid_generator)
        self.bidder = bidder
        self.item = auction_item
        self.bid_per_item = bid_per_item
        self.bid_limit = bid_limit
        
        # A bid cannot be negative
        try:
            assert self.bid_per_item >= 0
        except:
            print("bpi: {}".format(self.bid_per_item))
        # A limit cannot be non-positive 
        assert self.bid_limit >= 0
        # A bid cannot be bigger than its limit, since in the worst case a bidder could end up paying a price arbitrarily close to its bid.
        assert self.bid_per_item <= self.bid_limit

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.uid == other.uid

    def __hash__(self):
        return hash(self.__class__.__name__ + str(self.uid))

    def __repr__(self):
        return "{}(uid: {}, bidder: {}, auction_item_spec: {})".format(self.__class__.__name__, 
                                                                       self.uid, self.bidder, 
                                                                       self.auction_item_spec.uid)

    def deduct_limit(self, price: float):
        self.total_limit -= price

    @classmethod
    def from_vector(cls, bid_vec, bidder, auction_item_spec):
        '''
        Assuming bid vector is: [auction_item_spec_id, bid_per_item, total_limit].
        '''
        bid_per_item = bid_vec[1]
        total_limit = bid_vec[2]
        return cls(bidder, auction_item_spec, bid_per_item, total_limit)

    def to_vector(self):
        return [self.auction_item_spec.uid, self.bid_per_item, self.total_limit]

class Campaign:
    """
    Represents a campaign
    """
    _uid_generator = itertools.count(1)
    
    uid: int
    _reach: int
    _budget: float
    _target: MarketSegment # What segment to target

    def __init__(self, reach, target, start_day, end_day):
        self.uid = next(type(self)._uid_generator)
        self._reach = reach
        self._budget = None
        self._target = target
        self._start = start_day
        self._end = end_day
        self._costs = 0 
        self._impressions = 0
    
    @property 
    def start_day(self):
        return self._start
    
    @property 
    def end_day(self):
        return self._end

    @property
    def reach(self):
        return self._reach

    @property
    def budget(self):
        return self._budget

    @budget.setter 
    def budget(self, value):
        if self._budget is None:
            self._budget = value

    @property
    def target_segment(self):
        return self._target
    
    @property 
    def start(self):
        return self._start 
    
    @property 
    def end(self):
        return self._end
    
    @property 
    def cumulative_reach(self):
        return self._impressions 
    
    @cumulative_reach.setter 
    def cumulative_reach(self, impressions):
        self._impressions = impressions

    
    @property 
    def cumulative_cost(self):
        return self._costs

    @cumulative_cost.setter 
    def cumulative_cost(self, costs):
        self._costs = costs

    def __repr__(self):
        return "{}(uid: {}, reach: {}, budget: {}, target: {})".format(self.__class__.__name__,
                                                                       self.uid, self.reach, 
                                                                       self.budget, self.target)

    def __lt__(self, other):
        return (self.budget / self.reach) <= (other.budget / other.reach)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.uid == other.uid

    def __hash__(self):
        return hash(self.__class__.__name__ + str(self.uid))
    
class BidBundle:
    campaign_id: int 
    limit: float 
    bid_entries: Set[Bid]

    def __init__(self, campaign_id : int, limit : float, bid_entries : Set[Bid]):
        self.campaign_id = campaign_id 
        self.limit = limit 
        self.bid_entries = bid_entries 

    def __repr__(self):
        return f"BidBundle(id={self.campaign_id}, limit={self.limit}, bid_entries={self.bid_entries})"

