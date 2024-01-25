import argparse
from agt_server.agents.base_agents.bosii_agent import BOSIIAgent
from agt_server.local_games.bosii_arena import BOSIIArena


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


################### SUBMISSION #####################
agent_submission = ReluctantMoodAgent("Reluctant Mood Agent")
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

    agent = ReluctantMoodAgent(args.agent_name)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = BOSIIArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                ReluctantMoodAgent("Agent_1"),
                ReluctantMoodAgent("Agent_2"),
                ReluctantMoodAgent("Agent_3"),
                ReluctantMoodAgent("Agent_4")
            ]
        )
        arena.run()
