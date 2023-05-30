from agents.base_agents.chicken_agent import ChickenAgent
from agents.local_games.chicken_arena import ChickenArena
import argparse


class FloodNameAgent(ChickenAgent):
    def setup(self):
        self.SWERVE, self.CONTINUE = 0, 1
        self.actions = [self.SWERVE, self.CONTINUE]

    def get_action(self):
        return self.SWERVE

    def update(self):
        return None


if __name__ == "__main__":
    ##### EDIT THIS #####
    ip = '192.168.1.16'
    port = 1234

    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    parser.add_argument('--run_server', action='store_true',
                        help='Connects the agent to the server')

    args = parser.parse_args()

    agent = FloodNameAgent("a" * 2000)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = ChickenArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                FloodNameAgent("Agent_1"),
                FloodNameAgent("Agent_2"),
                FloodNameAgent("Agent_3"),
                FloodNameAgent("Agent_4")
            ]
        )
        arena.run()
