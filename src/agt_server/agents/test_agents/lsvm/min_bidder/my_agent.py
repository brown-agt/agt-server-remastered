from agt_server.agents.base_agents.lsvm_agent import MyLSVMAgent
from agt_server.local_games.lsvm_arena import LSVMArena
import time
class MinBidAgent(MyLSVMAgent):
    def setup(self):
        pass

    def get_bids(self):
        min_bids = self.get_min_bids()
        valuations = self.get_valuations() 
        bids = {}
        for good in valuations: 
            if valuations[good] > min_bids[good]:
                bids[good] = min_bids[good]
        return bids
    
    def update(self):
        pass

################### SUBMISSION #####################
my_agent_submission = MinBidAgent("Always Bid Min")
####################################################

if __name__ == "__main__":
    #### DO NOT TOUCH THIS #####
    agent = MinBidAgent("MY MIN BID AGENT")
    arena = LSVMArena(
        num_cycles_per_player = 3,
        timeout=1,
        # local_save_path="saved_games",
        players=[
            agent,
            MinBidAgent("Agent_1"),
            MinBidAgent("Agent_2"),
            MinBidAgent("Agent_3"),
            MinBidAgent("Agent_4"), 
            MinBidAgent("Agent_5"), 
            MinBidAgent("Agent_6"), 
        ]
    )
    
    start = time.time()
    arena.run()
    end = time.time()
    print(f"{end - start} Seconds Elapsed")

