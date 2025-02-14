from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np

LEARNING_RATE = 0.05
DISCOUNT_FACTOR = 0.90
EXPLORATION_RATE = 0.05


class CircularHotel(LemonadeAgent):
    def setup(self):
        self.num_states = range(144)
        self.starting_val = 0
        self.q_table = {
            s: [self.starting_val for _ in range(12)] for s in self.num_states}
        self.opp_1_acc = None
        self.opp_2_acc = None
        self.start = False
        self.state = None
        self.action = None

    def get_action(self):
        if self.start:
            state = self.opp_1_acc * 12 + self.opp_2_acc
            self.state = state
            try:
                action = np.argmax(self.q_table[state])
            except:
                action = random.randint(0, 11)
            self.action = action
            return action
        else:
            state = random.randint(0, 144)
            self.start = True
            self.state = state
            self.action = random.randint(0, 11)
            return self.action

    def update(self):
        self.opp_1_acc = self.get_opp1_last_action()
        self.opp_2_acc = self.get_opp2_last_action()
        try:
            self.q_table[self.state][self.action] += LEARNING_RATE * (
                self.get_last_util() + DISCOUNT_FACTOR *
                np.max(self.q_table[self.state])
                - self.q_table[self.state][self.action])
        except:
            pass

################### SUBMISSION #####################
agent_submission = CircularHotel("Circular Hotel")
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
                CircularHotel("Agent_1"),
                CircularHotel("Agent_2"),
                CircularHotel("Agent_3"),
                CircularHotel("Agent_4")
            ]
        )
        arena.run()
