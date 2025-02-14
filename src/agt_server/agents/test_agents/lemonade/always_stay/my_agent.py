from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random


class ReserveAgent(LemonadeAgent):
    def setup(self):
        self.my_spot = random.randint(0, 11)

    def get_action(self):
        return self.my_spot

    def update(self):
        return None

################### SUBMISSION #####################
agent_submission = ReserveAgent("Always Stay")
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
                ReserveAgent("Agent_1"),
                ReserveAgent("Agent_2"),
                ReserveAgent("Agent_3"),
                ReserveAgent("Agent_4")
            ]
        )
        arena.run()
