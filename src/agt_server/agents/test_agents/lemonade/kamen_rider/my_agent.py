from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np


class Kamen(LemonadeAgent):
    def setup(self):
        pass

    def get_action(self):
        try:
            if len(self.get_action_history()) < 50:
                return random.choice([2, 6, 10])
            else:
                my_acts = []

                possible_action1 = np.bincount(np.array(self.get_opp1_action_history()))
                possible_action2 = np.bincount(np.array(self.get_opp2_action_history()))

                possible_action1 = np.argpartition(possible_action1, -1)[-1:]
                possible_action2 = np.argpartition(possible_action2, -1)[-1:]

                for i, j in zip(possible_action1, possible_action2):
                    my_acts.append(self.find_action(i, j))

                return random.choice(my_acts)
        except:
            action = random.choice([10])
        return action

    def find_action(self, act1, act2):
        greatest_utils = []
        for position in range(12):
            temp = self.calculate_utility([act1, act2, position])
            greatest_utils.append(temp[-1])

        greatest_utils = np.array(greatest_utils)
        return np.random.choice(np.flatnonzero(greatest_utils == greatest_utils.max()))
    
    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = Kamen("Kamen")
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
                Kamen("Agent_1"),
                Kamen("Agent_2"),
                Kamen("Agent_3"),
                Kamen("Agent_4")
            ]
        )
        arena.run()
