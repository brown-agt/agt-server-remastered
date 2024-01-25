import argparse
from agt_server.agents.base_agents.bosii_agent import BOSIIAgent
from agt_server.local_games.bosii_arena import BOSIIArena


class ReluctantAgent(BOSIIAgent):
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
        if self.curr_state < 3:
            if opp_last_move == self.STUBBORN:
                self.curr_state += 1
            else:
                self.curr_state = 0
        else:
            self.curr_state = 0

################### SUBMISSION #####################
agent_submission = ReluctantAgent("Reluctant Agent")
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

    agent = ReluctantAgent(args.agent_name)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = BOSIIArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                ReluctantAgent("Agent_1"),
                ReluctantAgent("Agent_2"),
                ReluctantAgent("Agent_3"),
                ReluctantAgent("Agent_4")
            ]
        )
        arena.run()
