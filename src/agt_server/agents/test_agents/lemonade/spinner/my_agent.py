from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np


class Spinner(LemonadeAgent):
    def get_best_pos(self, a, b):
        ret = (a + b) // 2
        if min(abs((a - ret + 12) % 12), abs((ret - a + 12) % 12)) > 2:
            return ret
        else:
            return (ret + 6) % 12

    def setup(self):
        pass

    def get_action(self):
        try:
            last_opp_1 = self.get_opp1_action_history()[-1]
            last_opp_2 = self.get_opp2_action_history()[-1]
            action = random.choice([random.choice(
                [last_opp_1, last_opp_2]), self.get_best_pos(last_opp_1, last_opp_2)])
        except:
            action = random.choice([0, 4, 8])
        return action

    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = Spinner("Spinner")
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
                Spinner("Agent_1"),
                Spinner("Agent_2"),
                Spinner("Agent_3"),
                Spinner("Agent_4")
            ]
        )
        arena.run()
