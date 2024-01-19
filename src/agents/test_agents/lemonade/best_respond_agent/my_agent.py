from src.agents.base_agents.lemonade_agent import LemonadeAgent
from src.local_games.lemonade_arena import LemonadeArena
import argparse

class BestRespondAgent(LemonadeAgent):
    def __init__(self):
        super().__init__()
        self.next_action = 0
    
    def get_action(self):
        return self.next_action

    def update(self):
        l1 = self.get_opp1_last_action()
        l2 = self.get_opp2_last_action()
        if l1 == l2:
            self.next_action = (l1 + 6) % 12
        else:
            tmp = None
            if l1 < l2:
                tmp = l1
                l1 = l2
                l2 = tmp
            if (l1 - l2) > (12 - (l1 - l2)):
                self.next_action = (l1 - ((l1 + l2) // 2)) % 12
            else:
                self.next_action = (l1 + ((12 - (l1 - l2)) // 2)) % 12

if __name__ == "__main__":
    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--run_server', action='store_true',
                        help='Connects the agent to the server')
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help='IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port number (default: 8080)')

    args = parser.parse_args()

    agent = BestRespondAgent(args.agent_name)
    if args.run_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = LemonadeArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                BestRespondAgent("Agent_1"),
                BestRespondAgent("Agent_2"),
                BestRespondAgent("Agent_3"),
                BestRespondAgent("Agent_4")
            ]
        )
        arena.run()
