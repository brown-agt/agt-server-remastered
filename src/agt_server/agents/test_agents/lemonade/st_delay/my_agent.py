from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import time

class Thinker(LemonadeAgent):
    def setup(self):
        pass
    
    def get_action(self):
        time.sleep(5)
        return 5

    def update(self):
        pass


################### SUBMISSION #####################
agent_submission = Thinker("Delay")
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
                Thinker("Agent_1"),
                Thinker("Agent_2"),
                Thinker("Agent_3"),
                Thinker("Agent_4")
            ]
        )
        arena.run()
