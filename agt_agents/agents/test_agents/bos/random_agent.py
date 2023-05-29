import random
import argparse
from agents.base_agents.bos_agent import BOSAgent
from agents.local_games.bos_arena import BOSArena


class RandomAgent(BOSAgent):
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]

    def get_action(self):
        return random.choice(self.actions)

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

    agent = RandomAgent(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = BOSArena(players=[
            agent,
            RandomAgent("Agent_1"),
            RandomAgent("Agent_2"),
            RandomAgent("Agent_3"),
            RandomAgent("Agent_4")])
        arena.run()
