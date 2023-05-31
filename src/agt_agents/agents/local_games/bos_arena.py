from src.agt_agents.agents.local_games.base import LocalArena
from itertools import permutations


class BOSArena(LocalArena):
    def __init__(self, num_rounds=1000, players=[], timeout=1):
        super().__init__(num_rounds, players, timeout)
        self.game_name = "Battle of the Sexes"
        self.valid_actions = [0, 1]
        self.utils = [[(0, 0), (3, 7)],
                      [(7, 3), (0, 0)]]
        self.invalid_move_penalty = -1

        for idx in range(len(self.players)):
            player = self.players[idx]
            self.game_reports[player.name] = {
                "action_history": [],
                "util_history": [],
                "index": idx
            }
        import numpy as np
        self.result_table = np.zeros([len(players), len(players)])
        self.game_num = 1

    def reset_game_reports(self):
        for player in self.players:
            self.game_reports[player.name]["action_history"] = []
            self.game_reports[player.name]["util_history"] = []

    def run(self):
        for p1, p2 in permutations(self.players, 2):
            BOSArena.run_func_w_time(p1.setup, self.timeout, p1.name)
            BOSArena.run_func_w_time(p2.setup, self.timeout, p2.name)
            self.run_game(p1, p2)
        self.summarize_results()

    def run_game(self, p1, p2):
        p1.player_type = "bos_player"
        p2.player_type = "bos_player"
        for _ in range(self.num_rounds):
            p1_action = BOSArena.run_func_w_time(
                p1.get_action, self.timeout, p1.name, -1)
            p2_action = BOSArena.run_func_w_time(
                p2.get_action, self.timeout, p2.name, -1)
            self.game_reports[p1.name]['action_history'].append(p1_action)
            self.game_reports[p2.name]['action_history'].append(p2_action)

            if p1_action not in self.valid_actions and p2_action not in self.valid_actions:
                p1_util = 0
                p2_util = 0
            elif p1_action not in self.valid_actions:
                p1_util = self.invalid_move_penalty
                p2_util = 0
            elif p2_action not in self.valid_actions:
                p1_util = 0
                p2_util = self.invalid_move_penalty
            else:
                p1_util = self.utils[p1_action][p2_action][0]
                p2_util = self.utils[p1_action][p2_action][1]

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

            BOSArena.run_func_w_time(p1.update, self.timeout, p1.name)
            BOSArena.run_func_w_time(p2.update, self.timeout, p2.name)

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
            print(
                f"{p.name} was COOPERATIVE {action_counts[0]} times and STUBBORN {action_counts[1]} times")
            if action_counts[2] > 0:
                print(f"{p.name} submitted {action_counts[2]} invalid moves")
            total_util = sum(self.game_reports[p.name]['util_history'])

            avg_util = total_util / \
                len(self.game_reports[p.name]['util_history'])
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
        for d in self.result_table:
            means.append(sum(d) / (len(d) - 1))
        df['Mean Points'] = means
        df = df.sort_values('Mean Points', ascending=False)
        print(df)
