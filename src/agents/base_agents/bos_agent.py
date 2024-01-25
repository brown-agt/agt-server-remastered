from src.agents.base_agents.cm_agent import CompleteMatrixAgent
import json


class BOSAgent(CompleteMatrixAgent):
    def __init__(self, name=None):
        super().__init__(name)
        self.valid_actions = [0, 1]
        self.utils = [[(0, 0), (3, 7)],
                      [(7, 3), (0, 0)]]
        self.invalid_move_penalty = -1
        cfile = open("../../../../configs/server_configs/bos_config.json")
        server_config = json.load(cfile)
        self.response_time = server_config['response_time']

    def print_results(self):
        action_counts = [0 for _ in range(len(self.valid_actions) + 1)]
        for action in self.game_history['my_action_history']:
            if action in self.valid_actions:
                action_counts[action] += 1
            else:
                action_counts[2] += 1
        print(f"Game {self.game_num}:")
        if self.curr_opps: 
            print(f"I am currently playing against {', '.join(self.curr_opps[:-1]) + ', and ' + self.curr_opps[-1]}")
        print(
            f"{self.name} was COMPROMISING {action_counts[0]} times and was STUBBORN {action_counts[1]} times")
        if action_counts[2] > 0:
            print(f"{self.name} submitted {action_counts[2]} invalid moves")
        if self.global_timeout_count > 0:
            print(f"{self.name} timed out {self.global_timeout_count} times")
        total_util = sum(self.game_history['my_utils_history'])
        avg_util = total_util / len(self.game_history['my_utils_history'])

        print(
            f"{self.name} got a total utility of {total_util} and a average utility of {avg_util}")
        self.game_num += 1
