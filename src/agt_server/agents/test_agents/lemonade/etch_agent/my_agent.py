from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import math


class EtchAgent(LemonadeAgent):
    def setup(self):
        pass

    def get_action(self):
        try:
            last_opp_1 = self.get_opp1_action_history()[-1]
            last_opp_2 = self.get_opp2_action_history()[-1]
            action1 = (last_opp_1 + 6) % 12
            vals = 0
            for i in range(self.get_opp1_action_history()):
                val = math.abs(self.get_opp1_action_history()[
                               i] - self.get_opp2_action_history()[i])
                if (val > 6):
                    distance_away = val / 2
                else:
                    distance_away = (12 - val) / 2

                if (self.get_opp1_action_history()[i] > self.get_opp2_action_history()[i]):
                    bigger_val = self.get_opp1_action_history()[i]
                else:
                    bigger_val = self.get_opp2_action_history()[i]

                vals = vals + (bigger_val + distance_away) % 12

            val1 = math.abs(self.get_opp1_action_history()
                            [-1] - self.get_opp2_action_history()[-1])
            if (val1 > 6):
                distance_away1 = val / 2
            else:
                distance_away1 = (12 - val) / 2

            if (self.get_opp1_action_history()[-1] > self.get_opp2_action_history[-1]):
                bigger_val1 = self.get_opp1_action_history()[i]
            else:
                bigger_val1 = self.get_opp2_action_history()[i]

            val1 = val1 + (bigger_val1 + distance_away1) % 12

            action = (vals / len(self.get_opp1_action_history()) + val1) / 2

        except:
            action = random.choice([2])
        return action

    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = EtchAgent("Etch")
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
                EtchAgent("Agent_1"),
                EtchAgent("Agent_2"),
                EtchAgent("Agent_3"),
                EtchAgent("Agent_4")
            ]
        )
        arena.run()
