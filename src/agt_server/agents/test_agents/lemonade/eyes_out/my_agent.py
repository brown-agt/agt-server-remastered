from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random


class EyesOut(LemonadeAgent):
    def setup(self):
        pass

    def get_action(self):
        try:
            last_opp_1 = self.get_opp1_action_history()[-1]
            last_opp_2 = self.get_opp2_action_history()[-1]

            diff = abs(last_opp_1-last_opp_2)
            k = random.randint(0, 1)
            min_act = min(last_opp_1,last_opp_2)
            max_act = max(last_opp_1,last_opp_2)
            if diff >= 5 and diff <= 7:
                if diff <= 6:
                    action = (max_act + 4) % 12
                if diff == 7:
                    action = (max_act - 3) % 12
            elif diff == 4 or diff == 8:
                if diff == 8:
                    action = (min_act + 4) % 12
                if diff == 4:
                    action = (max_act + 4) % 12
            elif diff <= 3 or diff>=9:
                action = (max_act + 5) % 12
                if k == 1:
                    action = (min_act - 4) % 12
        except:
            action = random.choice([2])
        return action

    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = EyesOut("Etch")
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
                EyesOut("Agent_1"),
                EyesOut("Agent_2"),
                EyesOut("Agent_3"),
                EyesOut("Agent_4")
            ]
        )
        arena.run()
