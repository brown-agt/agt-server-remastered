from agt_server.agents.base_agents.lsvm_agent import MyLSVMAgent
from agt_server.local_games.lsvm_arena import LSVMArena
import time
class JumpBidder(MyLSVMAgent):
    def setup(self):
        pass

    def get_bids(self):
        min_bids = self.get_min_bids()
        valuations = self.get_valuations() 
        bids = {}
        for good in valuations: 
            if valuations[good] > min_bids[good]:
                bids[good] = valuations[good]
        return bids
    
    def update(self):
        pass

################### SUBMISSION #####################
my_agent_submission = JumpBidder("JumpBidder2")
####################################################

if __name__ == "__main__":
    #### DO NOT TOUCH THIS #####
    agent = JumpBidder("Truthful")
    arena = LSVMArena(
        num_cycles_per_player = 5,
        timeout=1,
        # local_save_path="saved_games",
        players=[
            agent,
            JumpBidder("Agent_1"),
            JumpBidder("Agent_2"),
            JumpBidder("Agent_3"),
            JumpBidder("Agent_4"), 
            JumpBidder("Agent_5"), 
            JumpBidder("Agent_6"), 
        ]
    )
    
    start = time.time()
    arena.run()
    end = time.time()
    print(f"{end - start} Seconds Elapsed")
