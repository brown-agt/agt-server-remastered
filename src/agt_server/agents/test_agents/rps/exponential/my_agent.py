from agt_server.agents.base_agents.rps_agent import RPSAgent
from agt_server.local_games.rps_arena import RPSArena
from agt_server.agents.test_agents.rps.ta_agent.my_agent import TAAgent
import argparse
import numpy as np


class ExponentialAgent(RPSAgent):
    def __init__(self, name):
        super(ExponentialAgent, self).__init__(name)
        self.setup()

    def setup(self):
        self.ROCK, self.PAPER, self.SCISSORS, = 0, 1, 2
        self.actions = [self.ROCK,  self.PAPER, self.SCISSORS]
        self.my_utils = np.zeros(len(self.actions))
        self.counts = [0, 0, 0]

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
        my_last_action = self.get_last_action()
        my_last_utility = self.get_last_util()
        self.my_utils[my_last_action] += my_last_utility
        self.counts[my_last_action] += 1

    def calc_move_probs(self):
        """
         Uses your historical average rewards to generate a probability distribution over your next move using
         the Exponential Weights strateg
        """
        # TODO Calculate the average reward for each action over time and return the softmax of it
        average_util = np.zeros(len(self.actions))
        for i, _ in enumerate(self.actions):
            average_util[i] = self.my_utils[i]
            if self.counts[i] != 0:
                average_util[i] = average_util[i] / self.counts[i]
        return self.softmax(average_util)


agent_submission = ExponentialAgent("EXP")

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
        arena = RPSArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                TAAgent("TA_Agent_1"),
                TAAgent("TA_Agent_2"),
                TAAgent("TA_Agent_3"),
                TAAgent("TA_Agent_4")
            ]
        )
        arena.run()
