from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np

class DelAgent(LemonadeAgent):
    def setup(self):
        self.choice = random.randint(0, 11)

    def get_action(self):
        if len(self.get_util_history()) > 10:
            utility = 0
            for i in range(10):
                utility += self.get_util_history()[-i]

            # we are doing worse than others
            if utility < 80:
                self.choice += 6
                if self.choice > 11:
                    self.choice = self.choice % 11

        return self.choice

    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = DelAgent("Del")
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
                DelAgent("Agent_1"),
                DelAgent("Agent_2"),
                DelAgent("Agent_3"),
                DelAgent("Agent_4")
            ]
        )
        arena.run()
