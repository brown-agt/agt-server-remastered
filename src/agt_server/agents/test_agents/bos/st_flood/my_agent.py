import argparse
from agt_server.agents.base_agents.bos_agent import BOSAgent
from agt_server.local_games.bos_arena import BOSArena


class FloodNameAgent(BOSAgent):
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]

    def get_action(self):
        return self.STUBBORN

    def update(self):
        pass


################### SUBMISSION #####################
agent_submission = None
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

    agent = FloodNameAgent("a" * 2000)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = BOSArena(
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
