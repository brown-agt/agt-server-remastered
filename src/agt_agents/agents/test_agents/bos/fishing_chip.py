import argparse
from src.agt_agents.agents.base_agents.bos_agent import BOSAgent
from src.agt_agents.agents.local_games.bos_arena import BOSArena


class FishingChip(BOSAgent):
    # You can ignore this test, it is just the agent that I implemented for the class competition moved from the trading platform to here
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]
        self.curr_state = 0

    def get_action(self):
        if self.curr_state == 10:
            return self.COMPROMISE
        else:
            return self.STUBBORN

    def update(self):
        opp_last_move = self.get_opp_last_action()
        if opp_last_move == self.STUBBORN:
            self.curr_state += 1
        else:
            self.curr_state = 0


if __name__ == "__main__":
    ##### EDIT THIS #####
    ip = '192.168.1.16'
    port = 1234

    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--run_server', action='store_true',
                        help='Connects the agent to the server')

    args = parser.parse_args()

    agent = FishingChip(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = BOSArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                FishingChip("Agent_1"),
                FishingChip("Agent_2"),
                FishingChip("Agent_3"),
                FishingChip("Agent_4")
            ]
        )
        arena.run()
