from agt_server.local_games.base import LocalArena
import numpy as np
from collections import defaultdict
import gzip
import json
from datetime import datetime
import pkg_resources
from elommr import EloMMR, Player, TanhTerm, PlayerEvent
import random
from copy import deepcopy
import pandas as pd
import os

class LSVMArena(LocalArena):
    def __init__(self, num_cycles_per_player = 3, players=[], timeout=1, handin=False, logging_path = None, save_path = None, elo_path = "local_elo_ranking.json", local_save_path = None, num_rounds = 1000):
        slack = 1000 
        random_number = np.random.exponential(scale=slack / 2)
        random_number_clipped = min(max(0, random_number), slack)
        num_rounds += random_number_clipped
        super().__init__(num_rounds, players, timeout, handin, logging_path, save_path)
        self.game_name = "Spectrum Auction - Local Synergy Value Model (LSVM)"
        self.num_cycles_per_player = num_cycles_per_player
        self.elommr = EloMMR()
        self.epsilon = 0.01
        self.current_prices = None
        self.min_bids = None
        self.tentative_winners = None
        self.tentative_winners_map = {}
        self.elo_path = elo_path
        self.local_save_path = local_save_path
    
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
                        "index": idx,
                        "timeout_count": 0,
                        "global_timeout_count": 0,
                        "disconnected": False, 
                        "elo": self.load_player_from_json(player.name)
                    }
                except:
                    continue
            else:
                player = self.players[idx]
                self.game_reports[player.name] = {
                    "bid_history": [],
                    "price_history": [],
                    "util_history": [],
                    "winner_history": [],
                    "index": idx,
                    "global_timeout_count": 0, 
                    "elo": self.load_player_from_json(player.name)
                }
        

        self.results = []
        self.game_num = 1
        
    def save_player_to_json(self, name, player):
        try:
            with open(self.elo_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        
        data[name] = {
            "_normal_factor": {"mu": player._normal_factor.mu, "sig": player._normal_factor.sig},
            "_logistic_factors": [{"mu": tht.mu, "w_arg": tht.w_arg, "w_out": tht.w_out} for tht in player._logistic_factors],
            "event_history": [{"rating_mu": ev.rating_mu, "rating_sig": ev.rating_sig, "perf_score": ev.perf_score, "place": ev.place} for ev in player.event_history],
            "approx_posterior": {"mu": player.approx_posterior.mu, "sig": player.approx_posterior.sig},
            "update_time": player.update_time,
            "delta_time": player.delta_time
        }
        
        with open(self.elo_path, 'w') as f:
            json.dump(data, f, indent=4)


    def load_player_from_json(self,name):
        with open(self.elo_path, 'r') as f:
            data = json.load(f)
        
        player = Player()
        if name in data:
            player_dict = data[name]
            player._normal_factor.mu = player_dict["_normal_factor"]["mu"]
            player._normal_factor.sig = player_dict["_normal_factor"]["sig"]
            player._logistic_factors = [TanhTerm(tht['mu'], tht['w_arg'], tht['w_out']) for tht in player_dict["_logistic_factors"]]
            player.event_history = [PlayerEvent(ev['rating_mu'], ev['rating_sig'], ev['perf_score'], ev['place']) for ev in player_dict["event_history"]]
            player.approx_posterior.mu = player_dict["approx_posterior"]["mu"]
            player.approx_posterior.sig = player_dict["approx_posterior"]["sig"]
            player.update_time = player_dict["update_time"]
            player.delta_time = player_dict["delta_time"]
        return player
    

    def reset_game_reports(self):
        for player in self.players:
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
        if len(self.game_reports[player_name]['elo'].event_history) > 0:   
            target_rating = self.game_reports[player_name]['elo'].event_history[-1].rating_mu
        else: 
            target_rating = 1600
        
        rating_diffs = {} 
        for name in self.game_reports: 
            if name != player_name: 
                if len(self.game_reports[name]['elo'].event_history) > 0:   
                    rating_diffs[name] = abs(self.game_reports[name]['elo'].event_history[-1].rating_mu - target_rating)
                else: 
                    rating_diffs[name] = 1600 - target_rating
        
        closest_matches = sorted(rating_diffs, key=rating_diffs.get)[:5]
        return set(closest_matches)
    
    # TODO: Update Leaderboard to also take in ELO.
    # TODO: Write a pygame visualizer to run through the files.
    # TODO: Connect the Code with gradescope and then cron it. 
    # TODO: pip install common packages like gym, tensorflow, pytorch, etc...
    # TODO: Connect the code with google drive to uplink the files to a shared drive with the students. 
    
    
    
    def run(self):
        """
        Simulates an LSVM auction with all of the players in self.players. 
        For each player, they are matched with the 5 other players closest in ELO to that player, 
        Then for the number of cycles each player plays, each player will cycle through being the national bidder once in a match 
        In each match the other regional bidders will be assigned one of the regional goods uniform at random. 
        Note that the regional bidders can be assigned the same regional good. 
        """
        for player in self.players:
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
                    curr_players[i].valuations = np.random.uniform(3, 9, shape)
                    curr_players[i]._current_round = self.current_round
                    for j in range(len(curr_players)): 
                        if i != j: 
                            curr_players[j]._is_national_bidder = False
                            curr_players[j].regional_good = np.random.choice(list("ABCDEFGHIJKLMNOPQR"))
                            curr_players[j].valuations = curr_players[j].proximity(np.random.uniform(3, 9, shape))
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
        Check if my_bids is a valid bid bundle and prunes the bids that are not valid.

        :param my_bids: Dictionary mapping goods to bid values.
        :return: True if the bid bundle is valid, False otherwise.
        """
        
        if not isinstance(my_bids, dict):
            return {}
        
        valid_bids = {}
        for good, bid in my_bids.items():
            if bid is None:
                continue

            if good not in player._goods_to_index or bid < player.min_bids[player._goods_to_index[good]]:
                continue

            price_history = player.game_report.game_history['price_history']
            bid_history = player.game_report.game_history['bid_history']
            revealed_preference = True
            my_bids_arr = player.map_to_ndarray(my_bids)
            if len(price_history) > 0 and len(bid_history) > 0: 
                past_prices = price_history[-1]
                past_bids = bid_history[-1]
                price_diff = player.current_prices - past_prices
                bid_diff = my_bids_arr - past_bids
                switch_cost = np.dot(price_diff.reshape(-1), bid_diff.reshape(-1))
                if switch_cost > 0:
                    revealed_preference = False 
                    break 
            
            if revealed_preference: 
                valid_bids[good] = bid
        return valid_bids 
    
    def run_helper(self, curr_players):
        has_incremental_goods = True
        rounds_so_far = 0
        while has_incremental_goods and rounds_so_far <= self.num_rounds: 
            rounds_so_far += 1
            has_incremental_goods = False
            if self.handin_mode:
                if any([self.game_reports[p.name]['disconnected'] for p in curr_players]):
                    return
                bids_this_round = defaultdict(lambda: [])
                for p in curr_players: 
                    p.current_prices = self.current_prices
                    p.min_bids = self.current_prices + self.epsilon
                    if self.game_reports[p.name]['timeout_count'] < self.timeout_tolerance: 
                        try:
                            self.run_func_w_time(
                                p.setup, self.timeout, p.name)
                            bids = self.run_func_w_time(
                                p.get_bids, self.timeout, p.name, {})
                            pruned_bids = LSVMArena.prune_valid_bids(p, bids)
                            for good in pruned_bids: 
                                bids_this_round[good].append((p.name, pruned_bids[good]))
                        except:
                            self.game_reports[p.name]['disconnected'] = True
                    else:
                        self.game_reports[p.name]['disconnected'] = True
                
                    self.game_reports[p.name]['bid_history'].append(bids)
                    p.game_report.game_history['bid_history_map'].append(bids)
                    p.game_report.game_history['bid_history'].append(p.map_to_ndarray(bids))
                    
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
                        winner_name = random.choice(winners)
                        winner = self.players[self.game_reports[winner_name]['index']]
                        winner_idx = winner._goods_to_index[good]
                        winner.tentative_allocation.add(good)
                        self.tentative_winners[winner_idx] = winner_name
                        self.tentative_winners_map[good] = winner_name
                        if len(sorted_bid_values) <= 1: 
                            self.current_prices[winner_idx] += self.epsilon
                        else: 
                            self.current_prices[winner_idx] = sorted_bid_values[1]
                
            else:
                bids_this_round = defaultdict(lambda: [])
                for p in curr_players: 
                    p.current_prices = self.current_prices
                    p.min_bids = self.current_prices + self.epsilon
                    self.run_func_w_time(
                        p.setup, self.timeout, p.name)
                    bids = self.run_func_w_time(
                        p.get_bids, self.timeout, p.name, {})
                    pruned_bids = LSVMArena.prune_valid_bids(p, bids)
                    for good in pruned_bids: 
                        bids_this_round[good].append((p.name, pruned_bids[good]))
                    self.game_reports[p.name]['bid_history'].append(bids)
                    p.game_report.game_history['bid_history_map'].append(bids)
                    p.game_report.game_history['bid_history'].append(p.map_to_ndarray(bids))
                    
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
                            self.current_prices[winner_idx] = sorted_bid_values[1]

            for p in curr_players: 
                prices_map = p.ndarray_to_map(p.current_prices)
                self.game_reports[p.name]['price_history'].append(prices_map)
                self.game_reports[p.name]['util_history'].append(p.calc_total_utility())
                self.game_reports[p.name]['winner_history'].append(self.tentative_winners_map)
                
                p.game_report.game_history['price_history'].append(p.current_prices)
                p.game_report.game_history['price_history_map'].append(prices_map)
                p.game_report.game_history['my_utils_history'].append(self.game_reports[p.name]['util_history'])
                p.game_report.game_history['winner_history'].append(self.tentative_winners)
                p.game_report.game_history['winner_history_map'].append(self.tentative_winners_map)

            self.current_round += 1
            for p in curr_players: 
                p._current_round = self.current_round
            
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
                        
    def run_game(self, curr_players):
        self.run_helper(curr_players)
        curr_player_names = [p.name for p in curr_players]
        curr_player_names_modified = [p.name + " (National)" if p.is_national_bidder() else p.name for p in curr_players]
        
        versus_str = f"Auction {self.game_num}: " + " VS ".join(curr_player_names_modified)
        print(f"{versus_str}")
        
        total_u = []
        for p in curr_players: 
            total_u.append(self.print_results(p))    
            
        player_utilities = sorted(zip(curr_player_names, total_u), key=lambda x: x[1], reverse=True)

        standings = []
        tie_start_index = 0

        for i in range(len(player_utilities)):
            if i == len(player_utilities) - 1 or player_utilities[i][1] != player_utilities[i + 1][1]:
                for j in range(tie_start_index, i + 1):
                    standings.append((player_utilities[j][0], tie_start_index, i))
                tie_start_index = i + 1 
                
        winner = player_utilities[0][0]       
        standings = [(self.game_reports[name]['elo'], start, end) for name, start, end in standings]
        self.elommr.round_update(standings)
        
        for p_name in curr_player_names: 
            self.save_player_to_json(p_name, self.game_reports[p_name]['elo'])
        
        sorted_zip = sorted(zip(curr_players, total_u), key=lambda x: x[0].name)
        sorted_players, sorted_total_u = zip(*sorted_zip)
        sorted_names = [p.name for p in sorted_players]
        self.results.append(sorted_names + list(sorted_total_u) + [winner])
        
        if self.local_save_path != None:
            now = datetime.now()
            timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"{timestamp_str}.json.gz"

            final_game_reports = deepcopy(self.game_reports)
            for player_name in final_game_reports: 
                player = self.players[final_game_reports[player_name]['index']]
                final_game_reports[player_name]['is_national_bidder'] = player.is_national_bidder()
                if player.valuations is not None:
                    final_game_reports[player_name]['valuations'] = player.ndarray_to_map(player.valuations)
                else: 
                    final_game_reports[player_name]['valuations'] = None
                if len(final_game_reports[player_name]['elo'].event_history) > 0:
                    final_game_reports[player_name]['elo'] = final_game_reports[player_name]['elo'].event_history[-1].display_rating()
                else: 
                    final_game_reports[player_name]['elo'] = f"{1600} ± {0}"
                final_game_reports[player_name]['regional_good'] = player.get_regional_good()
                    
            with gzip.open(f"{self.local_save_path}/{file_name}", 'wt', encoding='UTF-8') as f:
                json.dump(final_game_reports, f, indent=4)
        
        self.game_num += 1                 
        self.reset_game_reports()

    def print_results(self, p):
        if len(self.game_reports[p.name]['util_history']) > 0:
            final_util = self.game_reports[p.name]['util_history'][-1]
        else: 
            final_util = 0
        if len(p.tentative_allocation) > 0:
            print_smt = f"{p.name} won"
            print_smt += ",".join([f" Good {good} at Price {p.current_prices[p._goods_to_index[good]]:.2f}" for good in p.tentative_allocation])
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
        df = df.groupby(['Agent 1', 'Agent 2', 'Agent 3', 'Agent 4', 'Agent 5', 'Agent 6'])[['A1 Score', 'A2 Score', 'A3 Score', 'A4 Score', 'A5 Score', 'A6 Score']].mean().reset_index()

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
            if len( self.game_reports[key]['elo'].event_history) > 0:
                elo =  self.game_reports[key]['elo'].event_history[-1].rating_mu
            else: 
                elo = 1600
            if self.handin_mode and self.game_reports[key]['disconnected']:
                res_summary.append([key, float('-inf'), elo])
            elif value[1] > 0:
                res_summary.append(
                    [key, value[0] / value[1], elo])
            else:
                res_summary.append([key, 0, elo])

        sum_df = pd.DataFrame(res_summary)
        sum_df.columns = ['Agent Name', 'Final Score', 'ELO']
        sum_df = sum_df.sort_values('ELO', ascending=False)
        sum_df = sum_df[sum_df['Final Score'] != float('-inf')]
        
        if not self.handin_mode:
            print(f"Results: \n {sum_df}")
        else: 
            today_date_formatted = datetime.now().strftime('%Y-%m-%d_%H%M')
            final_str = f"{today_date_formatted}\t"
            result_list = [str(item) for group in zip(sum_df['Agent Name'], sum_df['Final Score'], sum_df['ELO']) for item in group]
            final_str += "\t".join(result_list)
            print(final_str)
            with open(pkg_resources.resource_filename('agt_server', self.save_path), 'a') as file:
                file.write(final_str + "\n")
            
        return sum_df
