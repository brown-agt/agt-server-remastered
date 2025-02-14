from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np


class HiBot(LemonadeAgent):
    def setup(self):
        self.opp_1_freq = np.zeros(12)
        self.opp_2_freq = np.zeros(12)
        self.alpha = 0.65


    def get_action(self):
        try:
            last_opp_1 = self.get_opp1_action_history()[-1]
            last_opp_2 = self.get_opp2_action_history()[-1]

            self.opp_1_freq *= self.alpha
            self.opp_2_freq *= self.alpha

            self.opp_1_freq[last_opp_1] += 1
            self.opp_2_freq[last_opp_2] += 1

            player_1_prob = np.exp(self.opp_1_freq) / np.sum(np.exp(self.opp_1_freq))
            player_2_prob = np.exp(self.opp_2_freq) / np.sum(np.exp(self.opp_2_freq))

            opp_1_exp = np.random.choice(np.arange(12), p=player_1_prob)
            opp_2_exp = np.random.choice(np.arange(12), p=player_2_prob)

            # opp_1_exp = np.argmax(self.opp_1_freq)
            # opp_2_exp = np.argmax(self.opp_2_freq)

            # rel = (opp_1_exp - opp_2_exp ) % 12

            if opp_1_exp >= opp_2_exp:
                greater = opp_1_exp
                rel = opp_1_exp - opp_2_exp
            else:
                greater = opp_2_exp
                rel = opp_2_exp - opp_1_exp

            if rel <= 6:
                action = (greater + 1) % 12
            else:
                action = (greater - 1) % 12

        except:
            action = np.random.choice(np.arange(12))
        return action

    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = HiBot("Hi")
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
                HiBot("Agent_1"),
                HiBot("Agent_2"),
                HiBot("Agent_3"),
                HiBot("Agent_4")
            ]
        )
        arena.run()
