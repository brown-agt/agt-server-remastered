from agt_server.agents.base_agents.chicken_agent import ChickenAgent
from agt_server.local_games.chicken_arena import ChickenArena
import argparse


class BasicAgent(ChickenAgent):
    def setup(self):
        self.SWERVE, self.CONTINUE = 0, 1
        self.actions = [self.SWERVE, self.CONTINUE]
        self.round = 0

    def get_action(self):
        if self.round % 3 == 0:
            return self.CONTINUE
        else:
            return self.SWERVE

    def update(self):
        self.round += 1

################### SUBMISSION #####################
agent_submission = BasicAgent("Basic Agent")
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

    agent = BasicAgent(args.agent_name)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = ChickenArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                BasicAgent("Agent_1"),
                BasicAgent("Agent_2"),
                BasicAgent("Agent_3"),
                BasicAgent("Agent_4")
            ]
        )
        arena.run()
