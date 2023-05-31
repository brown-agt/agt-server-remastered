from src.agt_agents.agents.base_agents.cm_agent import CompleteMatrixAgent


class RPSAgent(CompleteMatrixAgent):
    def print_results(self):
        action_counts = [0, 0, 0, 0]
        for action in self.game_history['my_action_history']:
            if action in [0, 1, 2]:
                action_counts[action] += 1
            else:
                action_counts[3] += 1
        print(f"Game {self.game_num}:")
        print(
            f"{self.name} played ROCK {action_counts[0]} times, SCISSORS {action_counts[1]} times, and PAPER {action_counts[2]} times")
        if action_counts[3] > 0:
            print(f"{self.name} submitted {action_counts[3]} invalid moves")
        total_util = sum(self.game_history['my_utils_history'])
        avg_util = total_util / len(self.game_history['my_utils_history'])

        print(
            f"{self.name} got a total utility of {total_util} and a average utility of {avg_util}")
        self.game_num += 1
