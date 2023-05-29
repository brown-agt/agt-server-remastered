import argparse
from agents.base_agents.rps_agent import RPSAgent
from agents.local_games.rps_arena import RPSArena
from agents.test_agents.rps.ta_agent import TAAgent


class BTAgent(RPSAgent):
    def setup(self):
        self.ROCK, self.SCISSORS, self.PAPER = 0, 1, 2
        self.actions = [self.ROCK, self.SCISSORS, self.PAPER]

    def get_action(self):
        return "This is an invalid move"

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

    agent = BTAgent(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = RPSArena(players=[
            agent,
            TAAgent("TA_Agent_1"),
            TAAgent("TA_Agent_2"),
            TAAgent("TA_Agent_3"),
            TAAgent("TA_Agent_4")])
        arena.run()
