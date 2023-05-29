import argparse
from agents.base_agents.bosii_agent import BOSIIAgent
from agents.local_games.bosii_arena import BOSIIArena

class PunitiveAgent(BOSIIAgent):
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.GOOD_MOOD, self.BAD_MOOD = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]
        self.curr_state = 0

    def get_action(self):
        if self.curr_state in [1, 3]:
            return self.COMPROMISE
        else:
            return self.STUBBORN

    def update(self):
        opp_last_move = self.get_opp_last_action()
        if self.curr_state == 0:
            if opp_last_move == self.STUBBORN:
                self.curr_state = 1
            else:
                self.curr_state = 0
        elif self.curr_state == 1:
            self.curr_state = 2
        elif self.curr_state == 2:
            if opp_last_move == self.STUBBORN:
                self.curr_state = 3
            else:
                self.curr_state = 2
        else:
            self.curr_state = 4


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

    agent = PunitiveAgent(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = BOSIIArena(players=[
            agent,
            PunitiveAgent("Agent_1"),
            PunitiveAgent("Agent_2"),
            PunitiveAgent("Agent_3"),
            PunitiveAgent("Agent_4")])
        arena.run()
