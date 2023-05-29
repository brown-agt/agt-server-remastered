import argparse
from agents.base_agents.bosii_agent import BOSIIAgent
from agents.local_games.bosii_arena import BOSIIArena


class CompromisingAgent(BOSIIAgent):
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.GOOD_MOOD, self.BAD_MOOD = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]

    def get_action(self):
        return self.COMPROMISE

    def update(self):
        return None


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

    agent = CompromisingAgent(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = BOSIIArena(players=[
            agent,
            CompromisingAgent("Agent_1"),
            CompromisingAgent("Agent_2"),
            CompromisingAgent("Agent_3"),
            CompromisingAgent("Agent_4")])
        arena.run()
