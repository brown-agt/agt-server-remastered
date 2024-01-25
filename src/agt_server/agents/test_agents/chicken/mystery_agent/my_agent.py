from agt_server.agents.base_agents.chicken_agent import ChickenAgent
from agt_server.local_games.chicken_arena import ChickenArena
import argparse
import random


class MysteryAgent(ChickenAgent):
    def setup(self):
        self.SWERVE, self.CONTINUE = 0, 1
        self.actions = [self.SWERVE, self.CONTINUE]
        self.round = 0

    def get_action(self):
        opp_action_hist = self.get_opp_action_history()
        if not opp_action_hist:
            return random.randint(0, 1)
        elif len(opp_action_hist) < 3:
            return random.randint(0, 1)
        else:
            j = len([x for x in opp_action_hist[-3:] if x == 1])
            if j > 1:
                return 1
            else:
                return 0

    def update(self):
        return None

################### SUBMISSION #####################
agent_submission = MysteryAgent("Mystery")
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
        arena = ChickenArena(
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
