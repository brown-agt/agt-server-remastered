from agt_server.local_games.base import LocalArena
from itertools import combinations
import numpy as np
import pandas as pd
import os
import json
from datetime import datetime


class RPSArena(LocalArena):
    def __init__(self, num_rounds=10, players=[], timeout=1, handin=False, 
                 logging_path=None, summary_path=None, detailed_reports_path=None):
        super().__init__(num_rounds, players, timeout, handin, logging_path, summary_path)
        self.game_name = "Rock, Paper, Scissors"
        self.valid_actions = [0, 1, 2]
        self.action_map = {0: "Rock", 1: "Paper", 2: "Scissors"}  # Map numbers to actions
        self.utils = [[0, -1, 1],  # Payoff matrix
                      [1, 0, -1],
                      [-1, 1, 0]]
        self.invalid_move_penalty = -1
        self.detailed_reports_path = detailed_reports_path

        if not self.handin_mode:
            assert len(self.players) >= 2, "Arena must have at least 2 players"

        for idx, player in enumerate(self.players):
            self.game_reports[player.name] = {
                "action_history": [],
                "util_history": [],
                "index": idx,
                "timeout_count": 0,
                "global_timeout_count": 0,
                "disconnected": False
            }

        self.result_table = np.zeros((len(players), len(players)))
        self.final_utilities = {player.name: 0 for player in self.players}
        self.game_num = 1

    def calculate_utils(self, p1_action, p2_action):
        if p1_action not in self.valid_actions and p2_action not in self.valid_actions:
            return [0, 0]
        if p1_action not in self.valid_actions:
            return [self.invalid_move_penalty, 0]
        if p2_action not in self.valid_actions:
            return [0, self.invalid_move_penalty]
        return [self.utils[p1_action][p2_action], self.utils[p2_action][p1_action]]

    def reset_game_reports(self):
        for player in self.players:
            self.game_reports[player.name]["action_history"] = []
            self.game_reports[player.name]["util_history"] = []

    def run_game(self, p1, p2):
        p1_total_util = 0
        p2_total_util = 0

        for _ in range(self.num_rounds):
            p1_action = self.run_func_w_time(p1.get_action, self.timeout, p1.name, -1)
            p2_action = self.run_func_w_time(p2.get_action, self.timeout, p2.name, -1)

            
            self.game_reports[p1.name]['action_history'].append(p1_action)
            self.game_reports[p2.name]['action_history'].append(p2_action)
            p1.game_report.game_history['my_action_history'].append(p1_action)
            p2.game_report.game_history['my_action_history'].append(p2_action)
            p1.game_report.game_history['opp_action_history'].append(p2_action)
            p2.game_report.game_history['opp_action_history'].append(p1_action)


            p1_util, p2_util = self.calculate_utils(p1_action, p2_action)
            self.game_reports[p1.name]['util_history'].append(p1_util)
            self.game_reports[p2.name]['util_history'].append(p2_util)
            p1.game_report.game_history['my_utils_history'].append(p1_util)
            p2.game_report.game_history['my_utils_history'].append(p2_util)
            p1.game_report.game_history['opp_utils_history'].append(p2_util)
            p2.game_report.game_history['opp_utils_history'].append(p1_util)

            p1_total_util += p1_util
            p2_total_util += p2_util
            self.run_func_w_time(p1.update, self.timeout, p1.name, -1)
            self.run_func_w_time(p2.update, self.timeout, p1.name, -1)

        # Update results table
        p1_index = self.game_reports[p1.name]["index"]
        p2_index = self.game_reports[p2.name]["index"]
        self.result_table[p1_index, p2_index] += p1_total_util
        self.result_table[p2_index, p1_index] += p2_total_util

        # Update final utilities
        self.final_utilities[p1.name] += p1_total_util
        self.final_utilities[p2.name] += p2_total_util

        # Summarize the game
        game_summary = self._generate_game_summary(p1, p2)
        self._log_or_print(game_summary)

        # Save detailed game report if needed
        if self.detailed_reports_path:
            self._save_detailed_game_report(p1, p2)

    def run(self):
        for p1, p2 in combinations(self.players, 2):
            self.run_func_w_time(p1.restart, self.timeout, p1.name)
            self.run_func_w_time(p2.restart, self.timeout, p2.name)
            self.run_game(p1, p2)
            self.game_num += 1

        return self.summarize_results()

    def summarize_results(self):
        agent_names = [player.name for player in self.players]
        df = pd.DataFrame(self.result_table, columns=agent_names, index=agent_names)

        # Add final and average utility columns
        df["Final Utility"] = [self.final_utilities[player.name] for player in self.players]
        df["Average Utility"] = df["Final Utility"] / (len(self.players) - 1)  # Average across opponents

        # Log or save results
        if self.save_path:
            df.to_csv(self.save_path)

        self._log_or_print("\nFinal Results:\n")
        self._log_or_print(df.to_string())

        return df

    def _generate_game_summary(self, p1, p2):
        """
        Generate a summary for a specific game between two players.
        """
        p1_actions = self.game_reports[p1.name]["action_history"]
        p2_actions = self.game_reports[p2.name]["action_history"]
        p1_utils = self.game_reports[p1.name]["util_history"]
        p2_utils = self.game_reports[p2.name]["util_history"]

        p1_action_counts = {action: p1_actions.count(action) for action in self.valid_actions}
        p2_action_counts = {action: p2_actions.count(action) for action in self.valid_actions}
        p1_invalid_moves = len([a for a in p1_actions if a not in self.valid_actions])
        p2_invalid_moves = len([a for a in p2_actions if a not in self.valid_actions])
        p1_total_utility = sum(p1_utils)
        p2_total_utility = sum(p2_utils)

        return (
            f"Game {self.game_num} Summary ({p1.name} VS {p2.name}):\n"
            f"{p1.name}: Played {p1_action_counts.get(0, 0)} Rocks, {p1_action_counts.get(1, 0)} Papers, "
            f"{p1_action_counts.get(2, 0)} Scissors; Invalid Moves: {p1_invalid_moves}; "
            f"Final Utility: {p1_total_utility}.\n"
            f"{p2.name}: Played {p2_action_counts.get(0, 0)} Rocks, {p2_action_counts.get(1, 0)} Papers, "
            f"{p2_action_counts.get(2, 0)} Scissors; Invalid Moves: {p2_invalid_moves}; "
            f"Final Utility: {p2_total_utility}.\n"
        )

    def _save_detailed_game_report(self, p1, p2):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}_game_{self.game_num}.json"
        report_path = os.path.join(self.detailed_reports_path, filename)

        report = {
            "game_number": self.game_num,
            "players": [p1.name, p2.name],
            "p1_history": self.game_reports[p1.name],
            "p2_history": self.game_reports[p2.name],
        }

        with open(report_path, "w") as f:
            json.dump(report, f, indent=4)

        self._log_or_print(f"Saved detailed report for Game {self.game_num} at {report_path}")
        

    def _log_message(self, message):
        """
        Log a message to the logging path if provided.
        """
        if self.logging_path:
            with open(self.logging_path, "a") as log_file:
                log_file.write(message + "\n")

    def _log_or_print(self, message):
        """
        Log or print the summary or final results.
        """
        if self.logging_path:
            self._log_message(message)
        else:
            print(message)
