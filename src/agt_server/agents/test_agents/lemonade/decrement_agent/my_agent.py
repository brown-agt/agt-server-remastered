from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse

class DecrementAgent(LemonadeAgent):
    def setup(self):
        self.loc = 0
        self.dec = 2
    
    def get_action(self):
        return self.loc

    def update(self):
        self.loc -= self.dec
        self.loc %= 12

################### SUBMISSION #####################
agent_submission = DecrementAgent("Dec")
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
                DecrementAgent("Agent_1"),
                DecrementAgent("Agent_2"),
                DecrementAgent("Agent_3"),
                DecrementAgent("Agent_4")
            ]
        )
        arena.run()
