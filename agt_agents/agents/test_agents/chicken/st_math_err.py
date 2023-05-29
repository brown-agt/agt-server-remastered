from agents.base_agents.chicken_agent import ChickenAgent
from agents.local_games.chicken_arena import ChickenArena
import argparse


class MathBreaker(ChickenAgent):
    def setup(self):
        self.SWERVE, self.CONTINUE = 0, 1
        self.actions = [self.SWERVE, self.CONTINUE]

    def get_action(self):
        a = 1 / 0
        return a

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

    agent = MathBreaker(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = ChickenArena(players=[
            agent,
            MathBreaker("Agent_1"),
            MathBreaker("Agent_2"),
            MathBreaker("Agent_3"),
            MathBreaker("Agent_4")])
        arena.run()
