from agt_server.agents.base_agents.gsvm_agent import GSVM9Agent 
from agt_server.local_games.gsvm_arena import GSVM9Arena
import time
import argparse

##################################
# Simple GSVM9Agent Definition
##################################
class BadSetup(GSVM9Agent):
    def setup(self):
        return 1/0

    def get_action(self):
        bids = {}
        for good, val in self.valuations.items():
            if val > 0:
                bids[good] = 2 * val
        
        return bids
    
    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = BadSetup("Bad Setup")
####################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='My GSVM9 Agent')
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
        arena = GSVM9Arena(
            num_rounds=3,
            players=[
                agent_submission,
                BadSetup("Agent_1"),
                BadSetup("Agent_2"),
                BadSetup("Agent_3"), 
                BadSetup("Agent_4"),
                BadSetup("Agent_5")
            ]
        )
        
        start = time.time()
        arena.run()
        end = time.time()
        print(f"{end - start} seconds elapsed.")
