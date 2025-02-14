from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np


class GoodBot(LemonadeAgent):
    def setup(self):
        pass

    def get_action(self):
        try:
            opp1_pos_mode = np.argmax(np.bincount(np.array(self.get_opp1_action_history())))
            opp2_pos_mode = np.argmax(np.bincount(np.array(self.get_opp2_action_history())))
            diff21 = (opp2_pos_mode - opp1_pos_mode) % 12
            diff12 = (opp1_pos_mode - opp2_pos_mode) % 12

            action = 0
            if diff21 > diff12:
                action = (opp1_pos_mode + diff21 // 2) % 12
            else:
                action = (opp2_pos_mode + diff12 // 2) % 12

            return action

        except:
            return random.randint(0, 11)

    def update(self):
        pass


################### SUBMISSION #####################
agent_submission = GoodBot("Good")
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
                GoodBot("Agent_1"),
                GoodBot("Agent_2"),
                GoodBot("Agent_3"),
                GoodBot("Agent_4")
            ]
        )
        arena.run()
