import random
from agt_server.local_games.base import LocalArena
import numpy as np
import pandas as pd 
from itertools import product, combinations

class SAArena(LocalArena):
    def __init__(self, num_goods, good_names = None, valuation_type = "additive", value_range = (0, 100), num_rounds=1000, players=[], timeout=1, handin=False, logging_path=None, save_path=None, kth_price = 1):
        super().__init__(num_rounds, players, timeout, handin, logging_path, save_path)
        self.num_goods = num_goods
        self.kth_price = kth_price

        if good_names is not None:
            if len(good_names) != num_goods:
                raise ValueError("Length of good_names must match num_goods")
            self._goods_to_index = {name: idx for idx, name in enumerate(good_names)}
            self.goods = set(good_names)
            self._index_to_goods = {idx: name for name, idx in self._goods_to_index.items()}
        else:
            self._goods_to_index = SAArena._name_goods(num_goods)
            self.goods = set(self._goods_to_index.keys())
            self._index_to_goods = {value: key for key, value in self._goods_to_index.items()}


        self.value_range = value_range 
        self.valuation_type = valuation_type
        self.game_name = "Simultaneous Auction"
        self.price_history = []
        self.winner_history = []
        
        if self.valuation_type == 'additive':
            self.valuation_multiplier = 1
        elif self.valuation_type == 'complement':
            self.valuation_multiplier = 1.2
        elif self.valuation_type == 'substitute':
            self.valuation_multiplier = 0.8
        elif self.valuation_type == 'randomized':
            self.valuation_multiplier = 1.2
        
        over_bidding_parameter = 1.25
        base_value = value_range[1] * num_goods
        self.bid_upper_bound = base_value * self.valuation_multiplier ** (num_goods - 1) * over_bidding_parameter

        for player in self.players: 
            player.bid_upper_bound = self.bid_upper_bound
            player.num_goods = self.num_goods
            player.goods = self.goods
            player._index_to_goods = self._index_to_goods  
            player._goods_to_index = self._goods_to_index
            player.valuation_type = self.valuation_type
            player.valuations = [0 for _ in range(self.num_goods)]

        assert len(self.players) >= 2, "Arena must have at least 2 players"

        for idx in range(len(self.players)):
            player = self.players[idx]
            self.game_reports[player.name] = {
                "valuation_history": [],
                "bid_history": [],
                "util_history": [],
                "index": idx,
                "global_timeout_count": 0
            }

        self.results = []
        self.game_num = 1

    def run(self):
        """
        Runs a single auction game in which all players participate.
        First, each agent is restarted, then the game runs for num_rounds rounds.
        Finally, the results are summarized.
        """

        self.run_game(self.players)
        
        results = self.summarize_results()
        return results

    def run_helper(self, group):
        for player in self.players:
            self.run_func_w_time(player.restart, self.timeout, player.name)
                    
        for _ in range(self.num_rounds):
            self._log_or_print(f"Game {self.game_num}: Auction Round - Goods: {self.goods}")
            
            pairwise_adjustments = {}
            if self.valuation_type == 'randomized':
                for good1, good2 in combinations(self.goods, 2):
                    pairwise_adjustments[(good1, good2)] = random.uniform(0.5, 1.5)

            for player in group:
                if self.valuation_type == 'randomized':
                    player.pairwise_adjustments = pairwise_adjustments
                
                valuations = {good: random.randint(self.value_range[0], self.value_range[1]) for good in self.goods}
                
                for good, value in valuations.items():
                    player.valuations[self._goods_to_index[good]] = value
                
                self.game_reports[player.name]['valuation_history'].append(valuations)

            bids = {}
            for player in group:
                bid = self.run_func_w_time(
                    lambda: player.get_action(),
                    self.timeout,
                    player.name,
                    None
                )
                self.game_reports[player.name]['bid_history'].append(bid)
                player.game_report.game_history['my_bid_history'].append(bid)
                
                
                bids[player.name] = bid
                
            for player in group: 
                player.game_report.game_history['opp_bid_history'].append([bids.get(p.name, None) for p in group if p != player])

            allocation, payments = self.compute_auction_result(bids)
            self.announce_outcome(allocation, payments)
            
            for player in group:
                player.game_report.game_history['my_payment_history'].append(payments[player.name])
                player.game_report.game_history['price_history'] = self.price_history
                player.game_report.game_history['winner_history'] = self.winner_history

            for player in group:
                won_goods = [good for good, winner in allocation.items() if winner == player.name] if allocation is not None else []
                valuations = self.game_reports[player.name]['valuation_history'][-1]
                
                base_sum = sum(valuations.get(good, 0) for good in won_goods)
                total_payment = payments[player.name]
                
                vt = self.valuation_type
                n = len(won_goods)
                
                if vt == 'additive':
                    round_val = base_sum
                elif vt == 'complement':
                    round_val = base_sum * (1 + 0.05 * (n - 1)) if n > 0 else 0
                elif vt == 'substitute':
                    round_val = base_sum * (1 - 0.05 * (n - 1)) if n > 0 else 0
                elif vt == 'randomized':
                    new_valuations = valuations.copy()
                    for good1, good2 in combinations(won_goods, 2):
                        multiplier = pairwise_adjustments.get((good1, good2), 1.0)
                        new_valuations[good1] *= multiplier
                        new_valuations[good2] *= multiplier
                    
                    round_val = sum(new_valuations.get(good, 0) for good in won_goods)
                else:
                    round_val = base_sum

                round_util = round_val - total_payment

                self.game_reports[player.name]['util_history'].append(round_util)
                player.game_report.game_history['my_utils_history'].append(round_util)


            for player in group:
                self.run_func_w_time(player.update, self.timeout, player.name)
            
            self.game_num += 1

    def compute_auction_result(self, bids):
        """
        Computes the auction outcome for each good individually.
        
        Each player's bid is assumed to be a dictionary mapping goods to bid values.
        For each good in self.goods:
        - Determine the highest bid (if any) among all players.
        - Award the good to the player with the highest bid.
        - That player pays the amount of their bid for that good.
        
        Returns:
            allocation: dict mapping each good to the winning player's name (or None if no valid bid).
            payments: dict mapping each player's name to their total payment (sum of bids on goods they won).
        """
        allocation = {}
        # Initialize payments for each player by their address.
        payments = {player.name: 0 for player in self.players}
        prices = {}

        for good in self.goods:
            bid_tuples = []
            # Collect all valid bids for the good.
            for addr, bid_bundle in bids.items():
                if bid_bundle is not None:
                    bid_value = bid_bundle.get(good, None)
                    if bid_value is not None and bid_value > 0:
                        bid_tuples.append((bid_value, addr))
            
            if bid_tuples:
                # Sort bids in descending order by bid value.
                sorted_bids = sorted(bid_tuples, key=lambda x: x[0], reverse=True)
                winner = sorted_bids[0][1]
                # Determine kth highest bid price.
                kth_index = self.kth_price - 1  # since list indices start at 0
                if kth_index < len(sorted_bids):
                    kth_bid = sorted_bids[kth_index][0]
                else:
                    # If there are fewer than kth bids, use the lowest bid available.
                    kth_bid = sorted_bids[-1][0]
            else:
                winner = None
                kth_bid = None
            
            allocation[good] = winner
            prices[good] = kth_bid
            if winner is not None and kth_bid is not None:
                payments[winner] += kth_bid

        self.price_history.append(prices)
        self.winner_history.append(allocation)
        return allocation, payments

    def announce_outcome(self, allocation, payments):
        """
        Announces the auction outcome.
        """
        message = f"Auction outcome:\n Allocation: {allocation} \n Payments: {payments}"
        self._log_or_print(message)
        return message

    def run_game(self, group):
        """
        Runs a full auction game for a given trio of players.
        If in handin mode, attempts to load a shortcut result; otherwise,
        it executes the auction rounds via run_helper.
        Then, prints each agent's results and updates the overall results.
        """
        self.run_helper(group)

    def print_results(self, p):
        """
        Prints and returns the total utility for a given agent.
        """
        total_util = sum(self.game_reports[p.name].get('util_history', []))
        print(f"{p.name} got a total auction utility of {total_util}")
        return total_util

    def summarize_results(self):
        summary_data = []

        for player in self.players:
            player_name = player.name
            util_history = self.game_reports[player_name].get('util_history', [])

            total_util = sum(util_history)
            avg_util = total_util / len(util_history) if util_history else 0

            summary_data.append([player_name, total_util, avg_util])

        df = pd.DataFrame(summary_data, columns=["Player", "Total Utility", "Avg Utility Per Round"])
        df = df.sort_values(by="Total Utility", ascending=False)

        print(f"\nFinal Auction Results after {self.game_num - 1} Rounds:\n", df)
        
        return df

    @staticmethod
    def _generate_sequence(alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        """
        Generates an infinite sequence of strings based on the provided alphabet.
        
        Parameters:
        - alphabet (str, optional): The alphabet to use for generating the sequence. Defaults to 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.
        
        Yields:
        - str: The next string in the sequence.
        """
        yield from alphabet 
        size = 2 
        while True:
            for letters in product(alphabet, repeat=size):
                yield ''.join(letters)
            size += 1
        
    @staticmethod
    def _name_goods(size, alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        """
        Names the goods in a multidimensional world of a given shape using an alphabet.
        
        Parameters:
        - size (int): The total number of goods to be named.
        - alphabet (str, optional): The alphabet used for naming goods.
        
        Returns:
        - dict: A mapping from string names to multidimensional indices.
        """
        alphabet_generator = SAArena._generate_sequence(alphabet)
        map_dict = {}
        
        for flat_index in range(size):
            letter = next(alphabet_generator)
            map_dict[letter] = flat_index
                        
        return map_dict