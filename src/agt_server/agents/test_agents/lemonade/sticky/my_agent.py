from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np


class Sticky(LemonadeAgent):

    def setup(self):
        self.move = random.randint(0, 11)  # choose a random initial location

    def get_action(self):
        # if this is not the first turn, check if opponents are trying to maximize or minimize distance
        if len(self.get_action_history()) > 0:
            opp_1_dist = (self.get_last_action() - self.get_opp1_action_history()[-1]) % 12  # calculate distance from opponent 1
            opp_2_dist = (self.get_last_action() - self.get_opp2_action_history()[-1]) % 12  # calculate distance from opponent 2

            # if both opponents are close (distance <= 3), assume they are trying to minimize distance
            if opp_1_dist <= 3 and opp_2_dist <= 3:
                # move to the opposite location (over the diagonal)
                self.move = (self.get_last_action() + 6) % 12

            # otherwise, assume they are trying to maximize distance and maintain current location

        # append the chosen action to the history and return it
        return self.move

    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = Sticky("Elmers")
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
                Sticky("Agent_1"),
                Sticky("Agent_2"),
                Sticky("Agent_3"),
                Sticky("Agent_4")
            ]
        )
        arena.run()
