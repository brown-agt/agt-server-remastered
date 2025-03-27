import random
import numpy as np
import pandas as pd
from collections import defaultdict
from agt_server.local_games.base import LocalArena
from itertools import permutations

class GSVM9Arena(LocalArena):
    def __init__(self,
                 kth_price = 1,
                 players=[],
                 num_rounds=10,
                 timeout=1,
                 handin=False,
                 logging_path=None,
                 save_path=None):
        """
        :param players: List of exactly 4 players [N, R1, R2, R3].
        :param num_rounds: Number of rounds in the repeated game.
        :param timeout: Timeout in seconds for get_action calls.
        :param handin: Boolean indicating whether to suppress prints and store logs in a file.
        :param logging_path: File path for logging if handin=True.
        :param save_path: Path for final results if handin=True.
        """
        super().__init__(num_rounds, players, timeout, handin, logging_path, save_path)

        # We expect exactly 4 players: 1 national, 3 regional.
        assert len(self.players) >= 4, "GSVM-9 requires at least 4 players."

        # Define the set of goods
        self.kth_price = kth_price
        self.goods = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        self.game_name = "GSVM-9 Auction"

        # Max valuations from the table (blank entries => 0 => not eligible)
        # By default, assume players[0] = National, players[1..3] = Regionals
        self.max_valuations = [
            # National Bidder
            {"A":15, "B":15, "C":30, "D":30, "E":15, "F":15, "G":0,  "H":0,  "I":0},
            # Regional Bidder 1
            {"A":20, "B":20, "C":40, "D":40, "E":20, "F":0,  "G":20, "H":0,  "I":0},
            # Regional Bidder 2
            {"A":0,  "B":40, "C":40, "D":20, "E":20, "F":0,  "G":0,  "H":20, "I":0},
            # Regional Bidder 3
            {"A":20, "B":20, "C":0,  "D":20, "E":20, "F":20, "G":0,  "H":0,  "I":20}
        ]

        # Capacity: National = 6, Regionals = 3
        self.capacity = [6, 3, 3, 3]

        # Initialize game reports
        for idx, player in enumerate(self.players):
            self.game_reports[player.name] = {
                "valuation_history": [],
                "bid_history": [],
                "util_history": [],
                "index": idx,
                "global_timeout_count": 0
            }

        self.results = []
        self.game_num = 1
        
        self.price_history = []
        self.winner_history = []

    def run(self):
        """
        Run the entire repeated auction for self.num_rounds rounds.
        """
        # Restart all agents first
        for group in permutations(self.players, 4):
            for player in self.players:
                self.run_func_w_time(player.restart, self.timeout, player.name)
                
            self.run_game(group)

        # Summarize final results
        results = self.summarize_results()
        return results

    def run_game(self, group):
        """
        Run all rounds of the auction among these 4 players.
        """
        self._log_or_print(f"\n{group[0].name} (National) vs. {group[1].name} (R1) vs. {group[2].name} (R2) vs. {group[3].name} (R3)")
        group[0]._is_national_bidder = True
        group[1]._is_national_bidder = False
        group[2]._is_national_bidder = False
        group[3]._is_national_bidder = False

        for _ in range(self.num_rounds):
            # 1) Assign valuations
            for i, player in enumerate(group):
                valuations = {}
                for good in self.goods:
                    max_val = self.max_valuations[i].get(good, 0)
                    if max_val > 0:
                        valuations[good] = random.uniform(0, max_val)
                    else:
                        valuations[good] = 0.0  # ineligible => 0
                # Store the valuations in the agent
                player.valuations = valuations
                # Save in game_reports
                self.game_reports[player.name]["valuation_history"].append(valuations)

            # 2) Gather bids
            bids = {}
            for player in group:
                bid_dict = self.run_func_w_time(player.get_action, self.timeout, player.name, {})
                if not isinstance(bid_dict, dict):
                    bid_dict = {}
                bids[player.name] = bid_dict
                self.game_reports[player.name]["bid_history"].append(bid_dict)

            # 3) Compute outcome (respect capacity)
            allocation, payments = self.compute_auction_result(bids, players=group)
            for player in group: 
                player.game_report.game_history["my_payment_history"].append(payments)
                player.game_report.game_history["price_history"].append(self.price_history[-1] if self.price_history else {})
                player.game_report.game_history["winner_history"].append(self.winner_history[-1] if self.winner_history else {})

            for i, player in enumerate(group):
                won_goods = [g for g, w in allocation.items() if w == player.name]
                base_sum = sum(player.valuations.get(g, 0) for g in won_goods)
                n = len(won_goods)
                synergy_val = (1 + 0.2*(n-1)) * base_sum if n > 0 else 0
                cost = payments[player.name]
                util = synergy_val - cost

                self.game_reports[player.name]["util_history"].append(util)

                if hasattr(player, 'game_report'):
                    if "my_utils_history" not in player.game_report.game_history:
                        player.game_report.game_history["my_utils_history"] = []
                    player.game_report.game_history["my_utils_history"].append(util)

            for player in group:
                self.run_func_w_time(player.update, self.timeout, player.name)

            self.game_num += 1

        for player in group: 
            player.print_results()

    def compute_auction_result(self, bids, players):
        allocation = {}
        payments = {p.name: 0 for p in players}
        prices = {}
        for good in self.goods:
            bid_tuples = []
            for addr, bid_bundle in bids.items():
                if bid_bundle is not None:
                    bid_value = bid_bundle.get(good, None)
                    if bid_value is not None and bid_value > 0:
                        bid_tuples.append((bid_value, addr))
            if bid_tuples:
                sorted_bids = sorted(bid_tuples, key=lambda x: x[0], reverse=True)
                winner = sorted_bids[0][1]
                kth_index = self.kth_price - 1
                if kth_index < len(sorted_bids):
                    kth_bid = sorted_bids[kth_index][0]
                else:
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

    def summarize_results(self):
        """
        Summarize results across all rounds:
        - total utility
        - average utility per round
        """
        summary_data = []
        for player in self.players:
            name = player.name
            util_list = self.game_reports[name]["util_history"]
            total_util = sum(util_list)
            avg_util = total_util / len(util_list) if util_list else 0
            summary_data.append([name, total_util, avg_util])

        df = pd.DataFrame(summary_data, columns=["Player", "Total Utility", "Avg Utility"])
        df = df.sort_values("Total Utility", ascending=False)
        self._log_or_print(f"\nFinal GSVM-9 Auction Results:\n{df}\n")
        return df
