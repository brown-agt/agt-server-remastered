from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random


class RandomAgent(LemonadeAgent):
    def setup(self):
        return None

    def get_action(self):
        return random.randint(0, 11)

    def update(self):
        return None

################### SUBMISSION #####################
agent_submission = RandomAgent("Rando")
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
                RandomAgent("Agent_1"),
                RandomAgent("Agent_2"),
                RandomAgent("Agent_3"),
                RandomAgent("Agent_4")
            ]
        )
        arena.run()
