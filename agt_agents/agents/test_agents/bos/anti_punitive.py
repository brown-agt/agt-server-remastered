import argparse
from agents.base_agents.bos_agent import BOSAgent
from agents.local_games.bos_arena import BOSArena


class AntiPunitiveAgent(BOSAgent):
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]
        self.curr_state = 0

    def get_action(self):
        if self.curr_state < 4: 
            return self.STUBBORN
        else:
            return self.COMPROMISE

    def update(self):
        self.curr_state += 1


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

    agent = AntiPunitiveAgent(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = BOSArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                AntiPunitiveAgent("Agent_1"),
                AntiPunitiveAgent("Agent_2"),
                AntiPunitiveAgent("Agent_3"),
                AntiPunitiveAgent("Agent_4")
            ])
        arena.run()
