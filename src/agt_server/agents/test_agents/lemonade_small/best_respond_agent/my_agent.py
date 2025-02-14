from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse

class BestRespondAgent(LemonadeAgent):
    def setup(self):
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

################### SUBMISSION #####################
agent_submission = BestRespondAgent("Best Response")
####################################################

if __name__ == "__main__":
    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    # parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--join_server', action='store_true',
                        help='Connects the agent to the server')
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help='IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port number (default: 8080)')

    args = parser.parse_args()

    if args.join_server:
        agent_submission.connect(ip=args.ip, port=args.port)
    else:
        arena = LemonadeArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent_submission,
                BestRespondAgent("Agent_1"),
                BestRespondAgent("Agent_2"),
                BestRespondAgent("Agent_3"),
                BestRespondAgent("Agent_4")
            ]
        )
        arena.run()
