from local_games.base import LocalArena
from itertools import combinations
import numpy as np


class ChickenArena(LocalArena):
    def __init__(self, num_rounds=1000, players=[], timeout=1, handin=False):
        super().__init__(num_rounds, players, timeout, handin)
        self.game_name = "Chicken"
        self.valid_actions = [0, 1]
        self.utils = [[(0, 0), (-1, 1)],
                      [(1, -1), (-5, -5)]]
        self.invalid_move_penalty = -5

        if not self.handin_mode:
            assert len(self.players) >= 2, "Arena must have at least 2 players"

        for idx in range(len(self.players)):
            if self.handin_mode:
                try:
                    player = self.players[idx]
                    self.game_reports[player.name] = {
                        "action_history": [],
                        "util_history": [],
                        "index": idx,
                        "timeout_count": 0,
                        "global_timeout_count": 0,
                        "disconnected": False
                    }
                except:
                    continue
            else:
                player = self.players[idx]
                self.game_reports[player.name] = {
                    "action_history": [],
                    "util_history": [],
                    "index": idx,
                    "global_timeout_count": 0
                }

        import numpy as np
        self.result_table = np.zeros([len(players), len(players)])
        self.game_num = 1

    def reset_game_reports(self):
        for player in self.players:
            if self.handin_mode:
                try:
                    self.game_reports[player.name]["action_history"] = []
                    self.game_reports[player.name]["util_history"] = []
                except:
                    continue
            else:
                self.game_reports[player.name]["action_history"] = []
                self.game_reports[player.name]["util_history"] = []

    def run(self):
        for p1, p2 in combinations(self.players, 2):
            if self.handin_mode:
                if self.game_reports[p1.name]['disconnected'] or self.game_reports[p2.name]['disconnected']:
                    continue
                else:
                    try:
                        self.run_func_w_time(
                            p1.setup, self.timeout, p1.name)
                    except:
                        self.game_reports[p1.name]['disconnected'] = True
                        continue

                    try:
                        self.run_func_w_time(
                            p2.setup, self.timeout, p2.name)
                    except:
                        self.game_reports[p2.name]['disconnected'] = True
                        continue

                    try:
                        self.run_game(p1, p2)
                    except:
                        self.reset_game_reports()
                        continue
            else:
                self.run_func_w_time(p1.setup, self.timeout, p1.name)
                self.run_func_w_time(p2.setup, self.timeout, p2.name)
                self.run_game(p1, p2)
        results = self.summarize_results()
        return results

    def calculate_utils(self, p1_action, p2_action):
        if p1_action not in self.valid_actions and p2_action not in self.valid_actions:
            utils = [0, 0]
        elif p1_action not in self.valid_actions:
            utils = [self.invalid_move_penalty, 0]
        elif p2_action not in self.valid_actions:
            utils = [0, self.invalid_move_penalty]
        else:
            utils = [self.utils[p1_action][p2_action][0],
                     self.utils[p1_action][p2_action][1]]
        return utils

    def run_game(self, p1, p2):
        p1.player_type = "chicken_player"
        p2.player_type = "chicken_player"
        for _ in range(self.num_rounds):
            if self.handin_mode:
                if self.game_reports[p1.name]['timeout_count'] < self.timeout_tolerance:
                    try:
                        p1_action = self.run_func_w_time(
                            p1.get_action, self.timeout, p1.name, -1)
                    except:
                        self.game_reports[p1.name]['disconnected'] = True
                        p1_action = -1
                else:
                    self.game_reports[p1.name]['disconnected'] = True
                    p1_action = -1

                if self.game_reports[p2.name]['timeout_count'] < self.timeout_tolerance:
                    try:
                        p2_action = self.run_func_w_time(
                            p2.get_action, self.timeout, p2.name, -1)
                    except:
                        self.game_reports[p2.name]['disconnected'] = True
                        p2_action = -1
                else:
                    self.game_reports[p2.name]['disconnected'] = True
                    p2_action = -1
            else:
                p1_action = self.run_func_w_time(
                    p1.get_action, self.timeout, p1.name, -1)
                p2_action = self.run_func_w_time(
                    p2.get_action, self.timeout, p2.name, -1)

            self.game_reports[p1.name]['action_history'].append(p1_action)
            self.game_reports[p2.name]['action_history'].append(p2_action)

            p1_util, p2_util = self.calculate_utils(p1_action, p2_action)

            self.game_reports[p1.name]['util_history'].append(p1_util)
            self.game_reports[p2.name]['util_history'].append(p2_util)

            p1.game_history['my_action_history'].append(p1_action)
            p1.game_history['my_utils_history'].append(p1_util)
            p1.game_history['opp_action_history'].append(p2_action)
            p1.game_history['opp_utils_history'].append(p2_util)

            p2.game_history['my_action_history'].append(p2_action)
            p2.game_history['my_utils_history'].append(p2_util)
            p2.game_history['opp_action_history'].append(p1_action)
            p2.game_history['opp_utils_history'].append(p1_util)

            if self.handin_mode:
                try:
                    self.run_func_w_time(p1.update, self.timeout, p1.name)
                except:
                    self.game_reports[p1.name]['disconnected'] = True

                try:
                    self.run_func_w_time(p2.update, self.timeout, p2.name)
                except:
                    self.game_reports[p2.name]['disconnected'] = True
            else:
                self.run_func_w_time(p1.update, self.timeout, p1.name)
                self.run_func_w_time(p2.update, self.timeout, p2.name)

        if not self.handin_mode:
            print(f"Game {self.game_num}:")
        for i in range(2):
            p = [p1, p2][i]
            op = [p2, p1][i]
            action_counts = [0, 0, 0]
            for action in self.game_reports[p.name]['action_history']:
                if action in [0, 1]:
                    action_counts[action] += 1
                else:
                    action_counts[2] += 1
            if not self.handin_mode:
                print(
                    f"{p.name} was COOPERATIVE {action_counts[0]} times and STUBBORN {action_counts[1]} times")
                if action_counts[2] > 0:
                    print(
                        f"{p.name} submitted {action_counts[2]} invalid moves")
                if self.game_reports[p.name]['global_timeout_count'] > 0:
                    print(
                        f"{p.name} timed out {self.game_reports[p.name]['global_timeout_count']} times")
                    self.game_reports[p.name]['global_timeout_count'] = 0
            total_util = sum(self.game_reports[p.name]['util_history'])

            avg_util = total_util / \
                len(self.game_reports[p.name]['util_history'])
            if not self.handin_mode:
                print(
                    f"{p.name} got a total utility of {total_util} and a average utility of {avg_util}")
            self.result_table[self.game_reports[p.name]['index'],
                              self.game_reports[op.name]['index']] += total_util
        self.game_num += 1
        self.reset_game_reports()

    def summarize_results(self):
        import pandas as pd
        df = pd.DataFrame(self.result_table)
        agent_names = [player.name for player in self.players]
        df.columns = agent_names
        df.index = agent_names
        means = []

        for pld, d in zip(self.game_reports.values(), self.result_table):
            if self.handin_mode and pld['disconnected']:
                means.append(float('-inf'))
            else:
                means.append(sum(d) / (len(self.result_table) - 1))

        df['Mean Points'] = means
        final_scores = [m / self.num_rounds for m in means]
        df['Final Score'] = final_scores
        df = df.sort_values('Mean Points', ascending=False)
        df = df[df['Mean Points'] != float('-inf')]
        if not self.handin_mode:
            print(df)
        return df
