from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import numpy as np


class Zenly(LemonadeAgent):
    def setup(self):
        self.state = 'sticky'
        self.tolerance = 5

    def transform(self, st):
        return 'fluid' if st == 'sticky' else 'sticky'

    def get_action(self):
        history1 = np.array([0] * 12)
        history2 = np.array([0] * 12)
        sight = min(40, len(self.get_action_history()))
        for i in range(sight):
            history1[self.get_opp1_action_history()[i]] += 1
            history2[self.get_opp2_action_history()[i]] += 1
        if max(history1) > sight / 3 and max(history2) > sight / 3:
            self.state = 'fluid'
            spot1 = np.random.choice(12, 1, p=history1 / np.sum(history1))
            spot1 = spot1[0]
            spot2 = np.random.choice(12, 1, p=history2 / np.sum(history2))
            spot2 = spot2[0]
            action = (np.random.choice(
                [spot1, spot2], 1, [0.5, 0.5])[0] + 6) % 12
            return action
        elif max(history1) <= sight / 4 and max(history2) <= sight / 4:
            return 5
        else:
            self.tolerance -= 1
            if self.tolerance < 0:
                self.state = self.transform(self.state)
                self.tolerance = 5
            if self.state == 'sticky':
                return 5
            if self.state == 'fluid':
                spot1 = np.random.choice(12, 1, p=history1 / np.sum(history1))
                spot1 = spot1[0]
                spot2 = np.random.choice(12, 1, p=history2 / np.sum(history2))
                spot2 = spot2[0]
                action = (np.random.choice(
                    [spot1, spot2], 1, [0.5, 0.5])[0] + 6) % 12
                return action

    def update(self):
        pass


################### SUBMISSION #####################
agent_submission = Zenly("Zenly")
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
                Zenly("Agent_1"),
                Zenly("Agent_2"),
                Zenly("Agent_3"),
                Zenly("Agent_4")
            ]
        )
        arena.run()
