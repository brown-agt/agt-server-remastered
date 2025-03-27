from agt_server.agents.base_agents.agent import Agent
from agt_server.agents.base_agents.game_report import GameReport
from agt_server.utils import extract_first_json
import json
import random
import numpy as np 
import pkg_resources
import threading
import pandas as pd
from itertools import combinations

class SimultaneousAuctionAgent(Agent):
    def __init__(self, name=None, timestamp=None):
        super().__init__(name, timestamp)
        config_path = pkg_resources.resource_filename('agt_server', 'configs/server_configs/sa_config.json')
        with open(config_path) as cfile:
            self.config = json.load(cfile)
        self.response_time = self.config['response_time']

        # To be set by the game
        self.num_goods = None
        self.valuation_type = None
        self.valuations = None
        self._goods_to_index = None
        self.goods = None
        self._index_to_goods = None
        self.round = 0 
        self.bid_upper_bound = None
        
        self.pairwise_adjustments = None 

    def timeout_handler(self):
        print(f"{self.name} has timed out")
        self.timeout = True

    def handle_permissions(self, resp):
        self.player_type = resp['player_type']
        self.game_report.game_history['my_bid_history'].append(resp['my_bid'])
        self.game_report.game_history['my_utils_history'].append(resp['my_util'])
        self.game_report.game_history['my_payment_history'].append(resp['payments'])
        self.game_report.game_history['price_history'].append(resp['prices'])
        self.game_report.game_history['winner_history'].append(resp['winners'])
        opp_bids = [bid for bid in resp['opp_bid_history'] if bid is not None]
        self.game_report.game_history['opp_bid_history'].append(opp_bids)
    
    def handle_postround_data(self, resp):
        self.global_timeout_count = resp['global_timeout_count']
        self.handle_permissions(resp)

    def get_action(self):
        # This should return the bid dictionary.
        return self.get_bids()
     
    def get_goods(self): 
        """
        Get the set of goods names available in the auction.
        """
        return self.goods 

    def get_num_goods(self): 
        """
        Get the total number of goods available.
        """
        return self.num_goods
    
    def get_goods_to_index(self): 
        """
        Get the mapping from goods names to their index.
        """
        return self._goods_to_index
    
    def calculate_valuation(self, goods):
        """
        Calculate the valuation for a given set of goods.
        """
        # Convert goods to indices if necessary
        
        if all(isinstance(good, str) for good in goods):
            goods = [self._goods_to_index[good] for good in goods]
        
        base_sum = np.sum([self.valuations[good] for good in goods])
        vt = self.valuation_type
        n = len(goods)

        if vt == 'additive':
            tot_val = base_sum
        elif vt == 'complement':
            tot_val = base_sum * (1 + 0.05 * (n - 1)) if n > 0 else 0
        elif vt == 'substitute':
            tot_val = base_sum * (1 - 0.05 * (n - 1)) if n > 0 else 0
        elif vt == 'randomized':
            new_valuations = self.valuations.copy()
            for good1, good2 in combinations(goods, 2):
                multiplier = self.pairwise_adjustments.get((good1, good2), 1.0)
                new_valuations[good1] *= multiplier
                new_valuations[good2] *= multiplier
            
            tot_val = sum(new_valuations[good] for good in goods)
        else:
            tot_val = base_sum
            
        return tot_val
    
    def get_valuation_as_array(self): 
        """
        Retrieves the agent's valuation as a numpy array.
        """
        return self.valuations
    
    def get_valuation(self, good): 
        """
        Retrieves the valuation for a specific good.
        """
        return self.valuations[self._goods_to_index[good]]
    
    def get_valuations(self, bundle=None): 
        """
        Retrieves the valuations for a set of goods.
        """
        if bundle is None: 
            bundle = self.goods
        return {good: self.valuations[self._goods_to_index[good]] for good in bundle}
    
    def get_game_report(self): 
        """
        Retrieves the game report.
        """
        return self.game_report
    
    def get_valuation_history(self):
        """
        Retrieves the valuation history.
        """
        return self.game_report.get_valuation_history()

    def get_util_history(self):
        """
        Retrieves the utility history.
        """
        return self.game_report.get_util_history()

    def get_bid_history(self): 
        """
        Retrieves the history of bids made.
        """
        return self.game_report.get_bid_history()
    
    def get_payment_history(self):
        """
        Retrieves the history of payments made.
        """
        return self.game_report.get_payment_history()
    
    def get_price_history(self):
        """
        Retrieves the history of prices.
        """
        return self.game_report.get_price_history()
    
    def get_winner_history(self): 
        """
        Retrieves the history of winners.
        """
        return self.game_report.get_winner_history()
    
    def get_opp_bid_history(self):
        """
        Retrieves the history of opponent bids.
        """
        return self.game_report.get_opp_bid_history()
    
    def get_last_opp_bids(self):
        """
        Retrieves the last bid made by opponents.
        """
        return self.game_report.get_last_opp_bids()
    
    def print_results(self):
        """
        Prints a summary of the current game results based on the game history.
        This includes details for the most recent round as well as cumulative statistics.
        """
        gh = self.game_report.game_history  # shorthand
        
        # Retrieve the most recent round data (if any)
        last_bid = gh.get('my_bid_history', [])[-1] if gh.get('my_bid_history') else None
        last_winners = gh.get('winner_history', [])[-1] if gh.get('winner_history') else None
        last_prices = gh.get('price_history', [])[-1] if gh.get('price_history') else None

        # Print the results for the most recent round
        if self.round > 0:
            print(f"Round {self.round} Results:")
            print("-----------------------------------------")
            print(f"Last Bid: {last_bid}")
            print(f"Winners: {last_winners}")
            print(f"Prices: {last_prices}")
            print("-----------------------------------------\n")
            
        self.round += 1
    def play(self):
        """
        Main loop for interacting with the Simultaneous Auction server.
        Listens for messages and responds appropriately:
          - Acknowledges preround data and updates auction parameters.
          - Responds to bid requests by sending its bid (via get_bids).
          - Handles round and game transitions.
          - Processes disqualification messages.
        """
        # Initial handshake (if any)
        data = self.client.recv(1024).decode()
        data = extract_first_json(data)
        if data:
            resp = json.loads(data)
            if resp.get('message') == 'provide_game_name':
                print(f"We are playing {resp.get('game_name')}")
                message = {"message": "game_name_recieved"}
                self.client.send(json.dumps(message).encode())
                self.restart()
        
        while True:
            data = self.client.recv(10000).decode()
            data = extract_first_json(data)
            if data:
                request = json.loads(data)
                if request.get('message') == 'send_preround_data':
                    # Update auction parameters from the server
                    self.player_type = request.get('player_type')
                    self.num_goods = request.get('num_goods')
                    goods_list = request.get('goods')
                    self.goods = set(goods_list)
                    valuations_dict = request.get('valuations')
                    raw_adjustments = request.get('pairwise_adjustments', {})
                    self.pairwise_adjustments = {tuple(key.split(',')): value for key, value in raw_adjustments.items()}
                    self.bid_upper_bound = request.get('bid_upper_bound')
                            
                    # Create goods mapping from the provided goods list
                    self._goods_to_index = {good: idx for idx, good in enumerate(goods_list)}
                    self._index_to_goods = {idx: good for good, idx in self._goods_to_index.items()}
                    self.valuations = np.zeros(self.num_goods)
                    for good, value in valuations_dict.items():
                        idx = self._goods_to_index[good]
                        self.valuations[idx] = value
                    message = {"message": "preround_data_recieved"}
                    self.client.send(json.dumps(message).encode())
                    continue
                elif request.get('message') == 'request_bid':
                    self.timeout = False
                    try:
                        timer = threading.Timer(self.response_time, self.timeout_handler)
                        timer.start()
                        bid = self.get_action()  # This should return your bid dictionary
                    finally:
                        if self.timeout:
                            bid = None
                        timer.cancel()
                    try:
                        message = {
                            "message": "provide_bid",
                            "bid": bid,
                            "timeout": self.timeout
                        }
                        self.client.send(json.dumps(message).encode())
                    except Exception as e:
                        print("Error sending bid:", e)
                elif request.get('message') == 'prepare_next_round':
                    self.print_results()
                    self.handle_postround_data(request)
                    self.update()
                    message = {"message": "ready_next_round"}
                    self.client.send(json.dumps(message).encode())
                elif request['message'] == 'game_end':
                    if request['send_results']:
                        try: 
                            df = pd.read_json(request['results'])
                            if df is not None:
                                print(df)
                        except: 
                            print("Results too large :(. Please check in with your Lab TA for the results")
                    else:
                        print(request['results'])
                    self.close()
                    break
                elif request.get('message') == 'disqualified':
                    if request.get('disqualification_message'):
                        print(request.get('disqualification_message'))
                    self.close()
                    break
