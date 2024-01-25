from agt_server.agents.base_agents.bosii_agent import BOSIIAgent
from agt_server.local_games.bosii_arena import BOSIIArena
import argparse
import numpy as np


class ExponentialAgent(BOSIIAgent):
    def __init__(self, name):
        super(ExponentialAgent, self).__init__(name)
        self.setup()

    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.GOOD_MOOD, self.BAD_MOOD = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]
        self.my_good_utils = [0, 0]
        self.good_counts = [0, 0]
        self.my_bad_utils = [0, 0]
        self.bad_counts = [0, 0]

    @staticmethod
    def softmax(x):
        # Shifting values to avoid nan issues (due to underflow)
        shifted_x = x - np.max(x)
        exp_values = np.exp(shifted_x)
        return exp_values/np.sum(exp_values)

    def get_action(self):
        move_p = self.calc_move_probs()
        my_move = np.random.choice(self.actions, p=move_p)
        return my_move

    def update(self):
        """
        HINT: Update your move history and utility history to help find your best move in calc_move_probs
        """
        action_history = self.get_action_history()
        util_history = self.get_util_history()
        mood_history = self.get_mood_history()

        self.my_good_utils = [0, 0]
        self.good_counts = [0, 0]
        self.my_bad_utils = [0, 0]
        self.bad_counts = [0, 0]

        for action, util, mood in zip(action_history, util_history, mood_history):
            if mood == self.GOOD_MOOD:
                self.my_good_utils[action] += util
                self.good_counts[action] += 1
            elif mood == self.BAD_MOOD:
                self.my_bad_utils[action] += util
                self.bad_counts[action] += 1

    def calc_move_probs(self):
        """
         Uses your historical average rewards to generate a probability distribution over your next move using
         the Exponential Weights strategy
        """
        # TODO Calculate the average reward for each action over time and return the softmax of it
        average_good_util = np.zeros(len(self.actions))
        average_bad_util = np.zeros(len(self.actions))

        for i, _ in enumerate(self.actions):
            average_good_util[i] = self.my_good_utils[i]
            if self.good_counts[i] != 0:
                average_good_util[i] = average_good_util[i] / \
                    self.good_counts[i]
            average_bad_util[i] = self.my_bad_utils[i]
            if self.good_counts[i] != 0:
                average_good_util[i] = average_good_util[i] / \
                    self.good_counts[i]

        average_util = np.zeros(len(self.actions))
        if self.is_row_player():
            for i in range(len(self.actions)):
                average_util[i] = self.col_player_good_mood_prob(
                ) * average_good_util[i] + (1 - self.col_player_good_mood_prob()) * average_bad_util[i]
        elif self.get_mood() == self.GOOD_MOOD:
            for i in range(len(self.actions)):
                average_util[i] = average_good_util[i]
        elif self.get_mood() == self.BAD_MOOD:
            for i in range(len(self.actions)):
                average_util[i] = average_bad_util[i]

        return self.softmax(average_util)

################### SUBMISSION #####################
agent_submission = ExponentialAgent("Exponential")
####################################################

if __name__ == "__main__":
    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--join_server', action='store_true',
                        help='Connects the agent to the server')
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help='IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port number (default: 8080)')

    args = parser.parse_args()

    agent = ExponentialAgent(args.agent_name)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = BOSIIArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                ExponentialAgent("Agent_1"),
                ExponentialAgent("Agent_2"),
                ExponentialAgent("Agent_3"),
                ExponentialAgent("Agent_4")
            ]
        )
        arena.run()
