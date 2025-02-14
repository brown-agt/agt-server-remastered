from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np


class Jimbus(LemonadeAgent):
    def setup(self):
        self.opp_1_freq = np.zeros(12)
        self.opp_2_freq = np.zeros(12)
        self.alpha = 0.65


    def get_action(self):
        if(len(self.get_opp1_action_history()) == 0):
            action = random.choice(np.arange(12))
        else:
            prob1s = np.bincount(self.get_opp1_action_history(), minlength=12)/len(self.get_opp1_action_history())
            prob2s = np.bincount(self.get_opp2_action_history(), minlength=12)/len(self.get_opp2_action_history())
            scores = np.zeros([12])
            for ours in range(12):
                for other in range(12):
                    dist = min(np.abs(ours-other), np.abs(12 + ours - other), np.abs(ours - other - 12))
                    scores[ours] += prob1s[other]*dist + prob2s[other]*dist
            action = np.argmax(scores)

        return action

    def update(self):
        pass


################### SUBMISSION #####################
agent_submission = Jimbus("Jimbus")
####################################################


if __name__ == "__main__":
    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    # parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--join_server', action='store_true',
                        help='Connects the agent to the server')
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help='IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port number (default: 8080)')

    args = parser.parse_args()

    if args.join_server:
        agent_submission.connect(ip=args.ip, port=args.port)
    else:
        arena = LemonadeArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent_submission,
                Jimbus("Agent_1"),
                Jimbus("Agent_2"),
                Jimbus("Agent_3"),
                Jimbus("Agent_4")
            ]
        )
        arena.run()
