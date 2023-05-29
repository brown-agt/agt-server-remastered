import argparse
from agents.base_agents.bosii_agent import BOSIIAgent
from agents.local_games.bosii_arena import BOSIIArena


class ReluctantMoodAgent(BOSIIAgent):
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.GOOD_MOOD, self.BAD_MOOD = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]
        self.curr_state = 0

    def get_action(self):
        if self.curr_state in [0, 1, 2]:
            return self.STUBBORN
        else:
            return self.COMPROMISE

    def update(self):
        opp_last_move = self.get_opp_last_action()
        opp_last_mood = self.get_last_mood()
        if self.is_row_player():
            if self.curr_state < 3:
                if opp_last_mood == self.BAD_MOOD and opp_last_move == self.STUBBORN:
                    self.curr_state += 1
                else:
                    self.curr_state = 0
            else:
                self.curr_state = 0
        else:
            if self.curr_state < 3:
                if opp_last_move == self.STUBBORN:
                    self.curr_state += 1
                else:
                    self.curr_state = 0
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

    agent = ReluctantMoodAgent(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = BOSIIArena(players=[
            agent,
            ReluctantMoodAgent("Agent_1"),
            ReluctantMoodAgent("Agent_2"),
            ReluctantMoodAgent("Agent_3"),
            ReluctantMoodAgent("Agent_4")])
        arena.run()
