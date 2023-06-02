from src.agt_agents.agents.base_agents.chicken_agent import ChickenAgent
from src.agt_agents.agents.local_games.chicken_arena import ChickenArena
import argparse


class SwerveAgent(ChickenAgent):
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
    parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--run_server', action='store_true',
                        help='Connects the agent to the server')

    args = parser.parse_args()

    agent = SwerveAgent(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = ChickenArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                SwerveAgent("Agent_1"),
                SwerveAgent("Agent_2"),
                SwerveAgent("Agent_3"),
                SwerveAgent("Agent_4")
            ]
        )
        arena.run()
