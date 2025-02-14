from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np


class QQQ(LemonadeAgent):
    def setup(self):
        self.state = None
        self.pos = None
        self.q_table = {(a, b): [10 for _ in range(12)]
                        for a in range(6) for b in range(6)}
        self.rel_mov_1 = []
        self.rel_mov_2 = []
        self.rel_actions = []
        self.lr = 0.9
        self.discount = 0.1
        self.explore = 0.5

    def test_consistent(self):
        opp1std = np.std(self.rel_mov_1)
        opp2std = np.std(self.rel_mov_2)
        return (opp1std <= 1, opp2std <= 1)

    def get_action(self):
       # TODO: Enter logic to pick next result here
        if self.state == None:
            self.pos = random.randint(0, 11)
        else:
            if random.random() < self.explore:
                action = random.randint(0, 11)
            else:
                action = np.argmax(self.q_table[self.state])
            # decrease explore chance
            self.explore *= 0.98
            self.pos = (self.pos + action) % 12
            self.rel_actions.append(action)
        return self.pos

    def update(self):
        opp1a = ((self.get_opp1_last_action() -
                 self.get_last_action()) % 12) // 2
        opp2a = ((self.get_opp2_last_action() -
                 self.get_last_action()) % 12) // 2
        if len(self.get_opp2_action_history()) > 1:
            self.rel_mov_1.append(
                (self.get_opp1_action_history()[-1] - self.get_opp1_action_history()[-2]) % 12)
            self.rel_mov_2.append(
                (self.get_opp1_action_history()[-1] - self.get_opp2_action_history()[-2]) % 12)
        new_state = (opp1a, opp2a)
        if self.state == None or len(self.rel_actions) == 0:
            self.state = new_state
            return
        last_action = self.rel_actions[-1]
        # make reward also somewhat value reducing opponent score
        utilities = self.calculate_utility(self.get_action_history(
        )[-1], self.get_opp1_action_history()[-1], self.get_opp2_action_history()[-1])
        new_reward = self.get_last_util() + (self.get_last_util() -
                                             max(utilities[1:])) / 2
        # update reward
        self.q_table[self.state][last_action] = (
            self.lr * (new_reward + self.discount *
                       np.max(self.q_table[new_state]))
            + (1 - self.lr) * self.q_table[self.state][last_action])
        # update state
        self.state = new_state

################### SUBMISSION #####################
agent_submission = QQQ("QQQ")
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
                QQQ("Agent_1"),
                QQQ("Agent_2"),
                QQQ("Agent_3"),
                QQQ("Agent_4")
            ]
        )
        arena.run()
