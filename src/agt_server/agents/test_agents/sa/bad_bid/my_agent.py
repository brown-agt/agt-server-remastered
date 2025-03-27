from agt_server.agents.base_agents.sa_agent import SimultaneousAuctionAgent 
from agt_server.local_games.sa_arena import SAArena
import time
import argparse

class BadBid(SimultaneousAuctionAgent):
    def setup(self):
        pass

    def get_action(self):
        return 1/0
    
    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = BadBid("Bad Bid")
####################################################
if __name__ == "__main__":
    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
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
        arena = SAArena(
            timeout=1,
            num_goods=3,
            players=[
                agent_submission,
                BadBid("Agent_1"),
                BadBid("Agent_2"),
                BadBid("Agent_3"),
                BadBid("Agent_4"), 
                BadBid("Agent_5"), 
                BadBid("Agent_6"), 
            ]
        )
        start = time.time()
        arena.run()
        end = time.time()
        print(f"{end - start} Seconds Elapsed")
