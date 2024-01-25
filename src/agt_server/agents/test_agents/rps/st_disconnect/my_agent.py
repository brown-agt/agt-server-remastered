import argparse
from agt_server.agents.base_agents.rps_agent import RPSAgent
from agt_server.local_games.rps_arena import RPSArena
from agt_server.agents.test_agents.rps.ta_agent.my_agent import TAAgent


class BadConnection(RPSAgent):
    def setup(self):
        self.ROCK, self.SCISSORS, self.PAPER = 0, 1, 2
        self.actions = [self.ROCK, self.SCISSORS, self.PAPER]

    def get_action(self):
        raise Exception("This is an exception happening")

    def update(self):
        return None


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

    agent = BadConnection(args.agent_name)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = RPSArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                TAAgent("TA_Agent_1"),
                TAAgent("TA_Agent_2"),
                TAAgent("TA_Agent_3"),
                TAAgent("TA_Agent_4")
            ]
        )
        arena.run()
