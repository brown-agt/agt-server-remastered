from agt_server.local_games.base import LocalArena
import numpy as np
from collections import defaultdict
import gzip
import json
from datetime import datetime
import pkg_resources
import random
from copy import deepcopy
import pandas as pd
import os
import math
from tqdm import tqdm

class LSVMArena(LocalArena):
    def __init__(self, num_cycles_per_player = 1, players=[], timeout=1, handin=False, logging_path = None, save_path = None, local_save_path = None, num_rounds = 1000):
        slack = 1000
        random_number = np.random.exponential(scale=slack / 2)
        random_number_clipped = min(max(0, random_number), slack)
        num_rounds += random_number_clipped
        num_rounds = math.ceil(num_rounds)
        super().__init__(num_rounds, players, timeout, handin, logging_path, save_path)
        self.game_name = "Spectrum Auction - Local Synergy Value Model (LSVM)"
        self.num_cycles_per_player = num_cycles_per_player
        self.epsilon = 0.1
        self.current_prices = None
        self.min_bids = None
        self.tentative_winners = None
        self.tentative_winners_map = {}
        self.local_save_path = local_save_path
        self.ignores = []
    
        if not self.handin_mode:
            assert len(self.players) >= 6, "Arena must have at least 6 players"
            player_names = [player.name for player in players]
            assert len(set(player_names)) == len(player_names), "Players must have unique names"

        for idx in range(len(self.players)):
            if self.handin_mode:
                try:
                    player = self.players[idx]
                    self.game_reports[player.name] = {
                        "bid_history": [],
                        "price_history": [],
                        "util_history": [],
                        "winner_history": [],
                        "invalid_bid_details": [], 
                        "index": idx,
                        "timeout_count": 0,
                        "global_timeout_count": 0,
                        "disconnected": False, 
                    }
                except:
                    self.players[idx] = None
                    continue
            else:
                player = self.players[idx]
                self.game_reports[player.name] = {
                    "bid_history": [],
                    "price_history": [],
                    "util_history": [],
                    "winner_history": [],
                    "invalid_bid_details": [], 
                    "index": idx,
                    "global_timeout_count": 0, 
                }
        

        self.results = []
        self.game_num = 1
    
    def set_ignores(self, ignores): 
        self.ignores = ignores

    def reset_game_reports(self):
        for player in self.players:
            if player is not None: 
                if self.handin_mode:
                    try:
                        self.game_reports[player.name]["bid_history"] = []
                        self.game_reports[player.name]["price_history"] = []
                        self.game_reports[player.name]["util_history"] = []
                        self.game_reports[player.name]["winner_history"] = []
                    except:
                        continue
                else:
                    self.game_reports[player.name]["bid_history"] = []
                    self.game_reports[player.name]["price_history"] = []
                    self.game_reports[player.name]["util_history"] = []
                    self.game_reports[player.name]["winner_history"] = []

    def _find_matches(self, player_name):
        assert player_name in self.game_reports, "Cannot match up a player that does not exist in the program."
        # if len(self.game_reports[player_name]['elo'].event_history) > 0:
        #     target_rating = self.game_reports[player_name]['elo'].event_history[-1].mu
        # else:
        #     target_rating = 400

        # rating_diffs = {}
        # for name in self.game_reports:
        #     if name != player_name and (not self.handin_mode or not self.game_reports[name]['disconnected']):
        #         if len(self.game_reports[name]['elo'].event_history) > 0:
        #             rating_diffs[name] = abs(self.game_reports[name]['elo'].event_history[-1].mu - target_rating)
        #         else:
        #             rating_diffs[name] = 400 - target_rating

        # TODO: See if ELO is fixable/integratable later
        if False:
            closest_matches = sorted(rating_diffs, key=rating_diffs.get)[:5]
            return set(closest_matches)
        else:
            all_possible_matches = list(set(self.game_reports.keys()) - {player_name})
            random_matches = random.sample(all_possible_matches, min(5, len(all_possible_matches)))
            return set(random_matches)
    
    
    def run(self):
        """
        Simulates an LSVM auction with all of the players in self.players. 
        For each player, they are matched with the 5 other players closest in ELO to that player, 
        Then for the number of cycles each player plays, each player will cycle through being the national bidder once in a match 
        In each match the other regional bidders will be assigned one of the regional goods uniform at random. 
        Note that the regional bidders can be assigned the same regional good. 
        """
        for player in self.players:
            if player is not None and player.name not in self.ignores: 
                for _ in range(self.num_cycles_per_player):
                    other_players = [self.players[self.game_reports[op_name]['index']] for op_name in self._find_matches(player.name)]
                    curr_players = other_players + [player]
                    for i in range(len(curr_players)): 
                        self.current_round = 0
                        shape = curr_players[i].get_shape()
                        self.current_prices = np.zeros(shape)
                        self.min_bids = np.zeros(shape)
                        self.tentative_winners = np.empty(shape, dtype=object)
                        self.tentative_winners_map = {}
                        curr_players[i]._is_national_bidder = True 
                        curr_players[i]._valuations = np.random.uniform(3, 9, shape)
                        curr_players[i]._current_round = self.current_round
                        for j in range(len(curr_players)): 
                            if i != j: 
                                curr_players[j]._is_national_bidder = False
                                curr_players[j]._regional_good = np.random.choice(list("ABCDEFGHIJKLMNOPQR"))
                                curr_players[j]._valuations = curr_players[j].proximity(np.random.uniform(3, 20, shape))
                                curr_players[j]._current_round = self.current_round
                        if self.handin_mode: 
                            if any([p is None or self.game_reports[p.name]['disconnected'] for p in curr_players]):
                                continue
                            else: 
                                for p in curr_players: 
                                    try:
                                        self.run_func_w_time(
                                            p.restart, self.timeout, p.name)
                                    except:
                                        self.game_reports[p.name]['disconnected'] = True
                                        continue
                            try:
                                self.run_game(curr_players)
                            except:
                                self.reset_game_reports()
                                continue
                        else: 
                            for p in curr_players: 
                                self.run_func_w_time(p.restart, self.timeout, p.name)
                            self.run_game(curr_players)
        results = self.summarize_results()
        return results

    @staticmethod
    def prune_valid_bids(player, my_bids):
        """
        Check if my_bids is a valid bid bundle and return only valid bids,
        while logging invalid ones and reasons.
        """
        if not isinstance(my_bids, dict):
            return {}

        valid_bids = {}
        invalid_reasons = {}

        my_bids_arr = player.map_to_ndarray(my_bids if my_bids else {})

        for good, bid in my_bids.items():
            if bid is None or not isinstance(bid, (int, float)):
                invalid_reasons[good] = "Invalid Type of Bid"
                continue

            if good not in player._goods_to_index:
                invalid_reasons[good] = f"Unknown good {good}"
                continue

            min_bid = player._min_bids[player._goods_to_index[good]]
            if bid < min_bid:
                invalid_reasons[good] = f"Below min bid ({bid:.2f} < {min_bid:.2f})"
                continue

            # REVEALED PREFERENCE CHECK
            price_history = player.game_report.game_history.get('price_history', [])
            bid_history = player.game_report.game_history.get('bid_history', [])
            revealed_preference = True

            if len(price_history) > 0 and len(bid_history) > 0:
                try:
                    past_prices = np.stack(price_history) 
                    past_bids = np.stack(bid_history)   

                    price_diffs = player._current_prices - past_prices  
                    bid_diffs = my_bids_arr - past_bids 

                    switch_costs = np.sum(price_diffs * bid_diffs, axis=1)
                    if np.any(switch_costs > 0):
                        revealed_preference = False
                except ValueError as e:
                    revealed_preference = False

            if not revealed_preference:
                invalid_reasons[good] = f"Revealed preference violated for good: {good}"
            else:
                valid_bids[good] = bid

        player.game_report.game_history.setdefault("invalid_bid_details", []).append(invalid_reasons)

        return valid_bids, invalid_reasons

    
    
    def run_helper(self, curr_players):
        has_incremental_goods = True
        rounds_so_far = 0
        pbar = tqdm(total = self.num_rounds, desc="Running Round", leave=False)
        if self.handin_mode:
            for p in curr_players: 
                try:
                    self.run_func_w_time(
                        p.setup, self.timeout, p.name)
                except:
                    self.game_reports[p.name]['disconnected'] = True
        else: 
            for p in curr_players:
                self.run_func_w_time(p.setup, self.timeout, p.name)
        
        while has_incremental_goods and rounds_so_far <= self.num_rounds: 
            rounds_so_far += 1
            pbar.update(1)
            has_incremental_goods = False
            if self.handin_mode:
                if any([self.game_reports[p.name]['disconnected'] for p in curr_players]):
                    return
                bids_this_round = defaultdict(lambda: [])
                for p in curr_players: 
                    p._current_prices = self.current_prices
                    p._min_bids = self.current_prices + self.epsilon
                    if self.game_reports[p.name]['timeout_count'] < self.timeout_tolerance: 
                        try:
                            bids = self.run_func_w_time(
                                p.get_bids, self.timeout, p.name, {})
                            pruned_bids, invalid_reasons = LSVMArena.prune_valid_bids(p, bids)
                            self.game_reports[p.name]['invalid_bid_details'].append(invalid_reasons)
                            for good in pruned_bids: 
                                bids_this_round[good].append((p.name, pruned_bids[good]))
                        except:
                            self.game_reports[p.name]['disconnected'] = True
                    else:
                        self.game_reports[p.name]['disconnected'] = True
                
                    self.game_reports[p.name]['bid_history'].append(pruned_bids)
                    p.game_report.game_history['bid_history_map'].append(pruned_bids)
                    p.game_report.game_history['bid_history'].append(p.map_to_ndarray(pruned_bids))
                    
                for p in curr_players: 
                    p.tentative_allocation = p.tentative_allocation - set(bids_this_round.keys())
                for good in bids_this_round: 
                    if len(bids_this_round[good]) > 0: 
                        bids = bids_this_round[good]
                        if len(bids) > 1: 
                            has_incremental_goods = True
                        
                        unique_bid_values = set([bid for _, bid in bids])
                        sorted_bid_values = sorted(list(unique_bid_values), reverse=True)
                        highest_bid = sorted_bid_values[0]
                        #print(good, sorted_bid_values, highest_bid)
                        winners = [name for name, bid in bids if bid == highest_bid]
                        #print(winners)
                        winner_name = random.choice(winners)
                        #print(winner_name)
                        winner = self.players[self.game_reports[winner_name]['index']]
                        winner_idx = winner._goods_to_index[good]
                        winner.tentative_allocation.add(good)
                        self.tentative_winners[winner_idx] = winner_name
                        self.tentative_winners_map[good] = winner_name
                        if len(sorted_bid_values) <= 1: 
                            self.current_prices[winner_idx] += self.epsilon
                        else: 
                            self.current_prices[winner_idx] = max(sorted_bid_values[1], self.current_prices[winner_idx] + self.epsilon)
                #         print(good, sorted_bid_values)
                # print(self.current_prices)
            else:
                bids_this_round = defaultdict(lambda: [])                
                for p in curr_players: 
                    p._current_prices = self.current_prices
                    p._min_bids = self.current_prices + self.epsilon
                    bids = self.run_func_w_time(
                        p.get_bids, self.timeout, p.name, {})
                    pruned_bids, invalid_reasons = LSVMArena.prune_valid_bids(p, bids)
                    self.game_reports[p.name]['invalid_bid_details'].append(invalid_reasons)
                    for good in pruned_bids: 
                        bids_this_round[good].append((p.name, pruned_bids[good]))
                    self.game_reports[p.name]['bid_history'].append(pruned_bids)
                    p.game_report.game_history['bid_history_map'].append(pruned_bids)
                    p.game_report.game_history['bid_history'].append(p.map_to_ndarray(pruned_bids))
                    
                for p in curr_players: 
                    p.tentative_allocation = p.tentative_allocation - set(bids_this_round.keys())
                for good in bids_this_round: 
                    if len(bids_this_round[good]) > 0: 
                        bids = bids_this_round[good]
                        if len(bids) > 1: 
                            has_incremental_goods = True
                        unique_bid_values = set([bid for _, bid in bids])
                        sorted_bid_values = sorted(list(unique_bid_values), reverse=True)
                        highest_bid = sorted_bid_values[0]
                        winners = [name for name, bid in bids if bid == highest_bid]
                        winner = random.choice(winners)
                        winner_name = random.choice(winners)
                        winner = self.players[self.game_reports[winner_name]['index']]
                        winner_idx = winner._goods_to_index[good]
                        winner.tentative_allocation.add(good)
                        self.tentative_winners[winner_idx] = winner_name
                        self.tentative_winners_map[good] = winner_name
                        if len(sorted_bid_values) <= 1: 
                            self.current_prices[winner_idx] += self.epsilon
                        else: 
                            self.current_prices[winner_idx] = max(sorted_bid_values[1], self.current_prices[winner_idx] + self.epsilon)

            # print(f"TENTATIVE WINNERS: {self.tentative_winners_map}")
            for p in curr_players: 
                prices_map = p.ndarray_to_map(p._current_prices)
                self.game_reports[p.name]['price_history'].append(prices_map)
                self.game_reports[p.name]['util_history'].append(p.calc_total_utility())
                self.game_reports[p.name]['winner_history'].append(deepcopy(self.tentative_winners_map))
                
                p.game_report.game_history['price_history'].append(p._current_prices)
                p.game_report.game_history['price_history_map'].append(prices_map)
                p.game_report.game_history['my_utils_history'].append(self.game_reports[p.name]['util_history'])
                p.game_report.game_history['winner_history'].append(self.tentative_winners)
                p.game_report.game_history['winner_history_map'].append(deepcopy(self.tentative_winners_map))

            self.current_round += 1
            for p in curr_players: 
                p._current_round = self.current_round
                p.game_report.game_history.setdefault("is_national_bidder", []).append(p.is_national_bidder())

            
            if self.handin_mode:
                for p in curr_players:
                    try:
                        self.run_func_w_time(p.update, self.timeout, p.name)
                    except:
                        self.game_reports[p.name]['disconnected'] = True
            else:
                for p in curr_players:
                    self.run_func_w_time(p.update, self.timeout, p.name)
                    self.run_func_w_time(p.update, self.timeout, p.name)
                    self.run_func_w_time(p.update, self.timeout, p.name)
        pbar.close()
                        
    def run_game(self, curr_players):
        curr_player_names = [p.name for p in curr_players]
        curr_player_names_modified = [p.name + " (National)" if p.is_national_bidder() else p.name for p in curr_players]
        
        versus_str = f"Auction {self.game_num}: " + " VS ".join(curr_player_names_modified)
        print(f"{versus_str}")
        
        if self.handin_mode: 
            with open(self.logging_path, 'a') as file:
                file.write(f"\n{versus_str}\n")
        
        self.run_helper(curr_players)
        
        total_u = []
        for p in curr_players: 
            total_u.append(self.print_results(p))    
            
        player_utilities = sorted(zip(curr_player_names, total_u), key=lambda x: x[1], reverse=True)

        standings = []
        tie_start_index = 0
        
        for i in tqdm(range(len(player_utilities)), desc = "Calculating Standings", leave=False):
            if i == len(player_utilities) - 1 or player_utilities[i][1] != player_utilities[i + 1][1]:
                for j in range(tie_start_index, i + 1):
                    standings.append((player_utilities[j][0], tie_start_index, i))
                tie_start_index = i + 1 
                
        winner = player_utilities[0][0]       
        # standings = [(self.game_reports[name]['elo'], start, end) for name, start, end in standings]
        # self.elommr.round_update(standings)
        
        sorted_zip = sorted(zip(curr_players, total_u), key=lambda x: x[0].name)
        sorted_players, sorted_total_u = zip(*sorted_zip)
        sorted_names = [p.name for p in sorted_players]
        self.results.append(sorted_names + list(sorted_total_u) + [winner])
        
        if self.local_save_path != None:
            file_name = f"{versus_str}.json.gz"

            final_game_reports = deepcopy(self.game_reports)
            for player_name in self.game_reports: 
                # print(player_name, len(final_game_reports[player_name]['winner_history']))
                if len(final_game_reports[player_name]['winner_history']) == 0 or (self.handin_mode and final_game_reports[player_name]['disconnected']):
                    del final_game_reports[player_name]
                    continue
                player = self.players[final_game_reports[player_name]['index']]
                final_game_reports[player_name]['is_national_bidder'] = player.is_national_bidder()
                if player._valuations is not None:
                    final_game_reports[player_name]['valuations'] = player.ndarray_to_map(player._valuations)
                else: 
                    final_game_reports[player_name]['valuations'] = None
                # if len(final_game_reports[player_name]['elo'].event_history) > 0:
                #     final_game_reports[player_name]['elo'] = final_game_reports[player_name]['elo'].event_history[-1].display_rating()
                # else: 
                #     final_game_reports[player_name]['elo'] = f"{400} ± {0}"
                final_game_reports[player_name]['regional_good'] = player.get_regional_good()
            
            with gzip.open(f"{self.local_save_path}/{file_name}", 'wt', encoding='UTF-8') as f:
                json.dump(final_game_reports, f, indent=4)
            print(f"File saved to {file_name}")
        
        self.game_num += 1                 
        self.reset_game_reports()

    def print_results(self, p):
        if len(self.game_reports[p.name]['util_history']) > 0:
            final_util = self.game_reports[p.name]['util_history'][-1]
        else: 
            final_util = 0
        if len(p.tentative_allocation) > 0:
            print_smt = f"{p.name} won"
            print_smt += ",".join([f" Good {good} at Price {p._current_prices[p._goods_to_index[good]]:.2f}" for good in p.tentative_allocation])
            print_smt += "."
            if self.handin_mode:
                with open(self.logging_path, 'a') as file:
                    file.write(f"{print_smt}\n")
            else: 
                print(f"{print_smt}")
        
        if not self.handin_mode:
            if self.game_reports[p.name]['global_timeout_count'] > 0:
                print(
                    f"{p.name} timed out {self.game_reports[p.name]['global_timeout_count']} times")
                self.game_reports[p.name]['global_timeout_count'] = 0
        
        if self.handin_mode:
            with open(self.logging_path, 'a') as file:
                    file.write(f"{p.name} got a final utility of {final_util}\n")
        else: 
            print(f"{p.name} got a final utility of {final_util}")
        return final_util

    def summarize_results(self):
        df = pd.DataFrame(self.results)
        df.columns = ['Agent 1', 'Agent 2', 'Agent 3', 'Agent 4', 'Agent 5', 'Agent 6',
                    'A1 Score', 'A2 Score', 'A3 Score', 'A4 Score', 'A5 Score', 'A6 Score', 
                    'Winner']

        df = df.groupby(['Agent 1', 'Agent 2', 'Agent 3', 'Agent 4', 'Agent 5', 'Agent 6'])[
            ['A1 Score', 'A2 Score', 'A3 Score', 'A4 Score', 'A5 Score', 'A6 Score']
        ].mean().reset_index()

        if self.handin_mode:
            with open(self.logging_path, 'a') as file:
                file.write(f"Extended Results: \n {df}")
        else:
            print(f"Extended Results: \n {df}")

        total_util_dict = defaultdict(lambda: [0, 0])
        for res in self.results:
            player_names = res[:6]
            utils = res[6:12]
            for name, util in zip(player_names, utils):
                total_util_dict[name][0] += util
                total_util_dict[name][1] += 1      

        res_summary = []
        for key, value in total_util_dict.items():
            if self.handin_mode and self.game_reports[key]['disconnected']:
                final_score = float('-inf')
            elif value[1] > 0:
                final_score = value[0] / value[1]
            else:
                final_score = 0
            res_summary.append([key, final_score])

        sum_df = pd.DataFrame(res_summary, columns=['Agent Name', 'Final Score'])
        sum_df = sum_df[sum_df['Final Score'] != float('-inf')]
        sum_df = sum_df.sort_values('Final Score', ascending=False)

        if not self.handin_mode:
            print(f"Results: \n {sum_df}")
        else:
            today_date_formatted = datetime.now().strftime('%Y-%m-%d_%H%M')
            final_str = f"{today_date_formatted}\t"
            result_list = [str(item) for group in zip(sum_df['Agent Name'], sum_df['Final Score']) for item in group]
            final_str += "\t".join(result_list)
            print(final_str)
            with open(pkg_resources.resource_filename('agt_server', self.save_path), 'a') as file:
                file.write(final_str + "\n")

        return sum_df