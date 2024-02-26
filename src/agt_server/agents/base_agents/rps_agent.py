from agt_server.agents.base_agents.cm_agent import CompleteMatrixAgent
import json
import pkg_resources


class RPSAgent(CompleteMatrixAgent):
    def __init__(self, name=None, timestamp=None):
        super().__init__(name, timestamp)
        self.valid_actions = [0, 1, 2]
        self.utils = [[(0, 0),(-1, 1), (1, -1)],
                      [(1, -1), (0, 0), (-1, 1)],
                      [(-1, 1), (1, -1), (0, 0)]]
        self.invalid_move_penalty = -1
        config_path = pkg_resources.resource_filename('agt_server', 'configs/server_configs/rps_config.json')
        with open(config_path) as cfile:
            server_config = json.load(cfile)
        self.response_time = server_config['response_time']

    def print_results(self):
        action_counts = [0, 0, 0, 0]
        for action in self.game_report.game_history['my_action_history']:
            if action in [0, 1, 2]:
                action_counts[action] += 1
            else:
                action_counts[3] += 1
        print(f"Game {self.game_num}:")
        if self.curr_opps: 
            and_str = ''
            if len(self.curr_opps) > 1: 
                and_str += ', and '
            print(f"I am currently playing against {', '.join(self.curr_opps[:-1]) + and_str + self.curr_opps[-1]}")
        print(
            f"{self.name} played ROCK {action_counts[0]} times, PAPER {action_counts[1]} times, and SCISSORS {action_counts[2]} times")
        if action_counts[3] > 0:
            print(f"{self.name} submitted {action_counts[3]} invalid moves")
        if self.global_timeout_count > 0:
            print(f"{self.name} timed out {self.global_timeout_count} times")
        total_util = sum(self.game_report.game_history['my_utils_history'])
        avg_util = total_util / len(self.game_report.game_history['my_utils_history'])

        print(
            f"{self.name} got a total utility of {total_util} and a average utility of {avg_util}")
        self.game_num += 1
