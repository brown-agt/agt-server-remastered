import argparse
from src.agt_agents.agents.base_agents.bos_agent import BOSAgent
from src.agt_agents.agents.local_games.bos_arena import BOSArena


class CompromisingAgent(BOSAgent):
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
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
        arena = BOSArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                CompromisingAgent("Agent_1"),
                CompromisingAgent("Agent_2"),
                CompromisingAgent("Agent_3"),
                CompromisingAgent("Agent_4")
            ]
        )
        arena.run()
