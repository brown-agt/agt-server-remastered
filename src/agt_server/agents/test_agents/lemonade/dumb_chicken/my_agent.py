from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np

class DumbChicken(LemonadeAgent):
    def setup(self):
        pass

    def get_action(self):
        if (len(self.get_opp1_action_history()) != 0):
            opp1 = np.floor(np.mean(np.array(self.get_opp1_action_history())))
            opp2 = np.floor(np.mean(np.array(self.get_opp2_action_history())))
            opp1_opp = (opp1 + 6) % 12
            opp2_opp = (opp2 + 6) % 12
            mean = (opp1_opp + opp2_opp) / 2
            action = np.floor(mean)
        else:
            action = random.randrange(12)
        return int(action)

    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = DumbChicken("Dumb")
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
                DumbChicken("Agent_1"),
                DumbChicken("Agent_2"),
                DumbChicken("Agent_3"),
                DumbChicken("Agent_4")
            ]
        )
        arena.run()
