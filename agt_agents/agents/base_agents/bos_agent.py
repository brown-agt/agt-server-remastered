from agents.base_agents.cm_agent import CompleteMatrixAgent


class BOSAgent(CompleteMatrixAgent):
    def print_results(self):
        action_counts = [0, 0, 0]
        for action in self.game_history['my_action_history']:
            if action in [0, 1]:
                action_counts[action] += 1
            else:
                action_counts[2] += 1
        print(f"Game {self.game_num}:")
        print(
            f"{self.name} was COMPROMISING {action_counts[0]} times and was STUBBORN {action_counts[1]} times")
        if action_counts[2] > 0:
            print(f"{self.name} submitted {action_counts[2]} invalid moves")
        total_util = sum(self.game_history['my_utils_history'])
        avg_util = total_util / len(self.game_history['my_utils_history'])

        print(
            f"{self.name} got a total utility of {total_util} and a average utility of {avg_util}")
        self.game_num += 1
