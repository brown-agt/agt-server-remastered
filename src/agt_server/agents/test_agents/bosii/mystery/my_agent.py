import argparse
from agt_server.agents.base_agents.bosii_agent import BOSIIAgent
from agt_server.local_games.bosii_arena import BOSIIArena


class MysteryAgent(BOSIIAgent):
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.GOOD_MOOD, self.BAD_MOOD = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]
        self.curr_state = 0

    def get_action(self):
        if self.is_row_player():
            if self.curr_state == 0:
                return self.STUBBORN
            elif self.curr_state == 1:
                return self.COMPROMISE
        else:
            if self.curr_state == 0:
                return self.STUBBORN
            elif self.curr_state == 1:
                if self.get_mood() == self.GOOD_MOOD:
                    return self.COMPROMISE
                elif self.get_mood() == self.BAD_MOOD:
                    return self.STUBBORN
            elif self.curr_state == 2:
                return self.COMPROMISE

    def update(self):
        opp_last_move = self.get_opp_last_action()
        last_mood = self.get_last_mood()
        if self.is_row_player():
            if self.curr_state == 0:
                if opp_last_move == self.STUBBORN and last_mood == self.BAD_MOOD:
                    self.curr_state = 1
                if opp_last_move == self.COMPROMISE and last_mood == self.GOOD_MOOD:
                    self.curr_state = 1
            elif self.curr_state == 1:
                if opp_last_move == self.STUBBORN and last_mood == self.BAD_MOOD:
                    self.curr_state = 0
                if opp_last_move == self.COMPROMISE and last_mood == self.GOOD_MOOD:
                    self.curr_state = 0
        else:
            if self.curr_state == 0:
                if opp_last_move == self.COMPROMISE:
                    self.curr_state = 1
            elif self.curr_state == 1:
                if last_mood == self.GOOD_MOOD:
                    self.curr_state = 0
                elif last_mood == self.BAD_MOOD:
                    self.curr_state = 2
            elif self.curr_state == 2:
                if opp_last_move == self.STUBBORN:
                    self.curr_state = 1

################### SUBMISSION #####################
agent_submission = MysteryAgent("Mystery Agent")
####################################################

if __name__ == "__main__":
    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--join_server', action='store_true',
                        help='Connects the agent to the server')
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help='IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port number (default: 8080)')

    args = parser.parse_args()

    agent = MysteryAgent(args.agent_name)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = BOSIIArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                MysteryAgent("Agent_1"),
                MysteryAgent("Agent_2"),
                MysteryAgent("Agent_3"),
                MysteryAgent("Agent_4")
            ]
        )
        arena.run()
