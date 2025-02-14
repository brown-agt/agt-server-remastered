from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np


class E2Agent(LemonadeAgent):
    def setup(self):
        self.gamma = 0.75
        self.rho = 0.5
        self.tol = 0.1
        self.stick = 5
        self.t = 0
        self.carrot_stick = 0
        self.prev_action = random.randint(0, 11)

    def distance(self, loc1, loc2):
        return min((loc1 - loc2) % 12, (loc2 - loc1) % 12) ** self.rho

    def opposite(self, loc):
        return (loc + 6) % 12

    def teehee(self, idx, time_idx):
        if (idx == 0):
            return self.get_action_history()[time_idx]
        elif (idx == 1):
            return self.get_opp1_action_history()[time_idx]
        else:
            return self.get_opp2_action_history()[time_idx]

    def compute_indices(self):
        """
        Trust wont be called before self.t is invalid heh
        """
        # stick indices
        self.gammas = []
        cur_gamma = 1
        gamma_sum = 0
        for i in range(1, self.t):
            self.gammas.append(cur_gamma)
            gamma_sum += cur_gamma
            cur_gamma *= self.gamma
        self.gammas.reverse()

        s1, s2 = (0, 0)
        for i in range(1, self.t):
            s1 -= self.gammas[i - 1] / gamma_sum * self.distance(self.get_opp1_action_history()[i],
                                                                 self.get_opp1_action_history()[i - 1])
            s2 -= self.gammas[i - 1] / gamma_sum * self.distance(self.get_opp2_action_history()[i],
                                                                 self.get_opp2_action_history()[i - 1])

        # now compute
        follow_cross = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            for j in range(3):
                if (i == j):
                    continue
                for k in range(1, self.t):
                    i_act = self.teehee(i, k)
                    j_act = self.teehee(j, k - 1)
                    follow_cross[i][j] -= self.gammas[k - 1] / \
                        gamma_sum * self.distance(i_act, self.opposite(j_act))
        f1, f2 = (0, 0)

        for i in range(1, self.t):
            f1 -= self.gammas[i - 1] / gamma_sum * min(
                self.distance(self.teehee(1, i), self.opposite(
                    self.teehee(0, i - 1))),
                self.distance(self.teehee(1, i),
                              self.opposite(self.teehee(2, i - 1)))
            )
            f2 -= self.gammas[i - 1] / gamma_sum * min(
                self.distance(self.teehee(2, i), self.opposite(
                    self.teehee(0, i - 1))),
                self.distance(self.teehee(2, i),
                              self.opposite(self.teehee(1, i - 1)))
            )
        return s1, s2, follow_cross, f1, f2

    def calc_bias(self, target_opp, stick_opp_loc):
        acts = None
        if target_opp == 1:
            acts = self.get_opp1_action_history()
        else:
            acts = self.get_opp1_action_history()

        # calculate a bias
        opp = self.opposite(stick_opp_loc)
        bias = 0
        for i in range(len(acts)):
            if i > opp or i < acts[i]:
                # its on the "left"
                bias -= 1
            elif i < opp or i > acts[i]:
                bias += 1
        return bias

    def get_action(self):
        if self.t > 0:
            last_opp_1 = self.get_opp1_action_history()[-1]
            last_opp_2 = self.get_opp2_action_history()[-1]
            prev_util = self.get_util_history()[-1]

        if self.stick > 0:
            self.stick -= 1
            return self.prev_action

        if self.carrot_stick > 0:
            # move yourself to the side a bit
            self.carrot_stick -= 1
            if self.carrot_stick > 3:
                return self.prev_action
            if self.bias:
                self.prev_action = (self.prev_action + 1) % 12
            else:
                self.prev_action = (self.prev_action - 1) % 12
            return self.prev_action

        s1, s2, follow_cross, f1, f2 = self.compute_indices()
        if s1 > max(max(f1, s2), f2) + self.tol:
            self.prev_action = self.opposite(last_opp_1)
        elif s2 > max(max(f1, s1), f2) + self.tol:
            self.prev_action = self.opposite(last_opp_2)
        elif s1 > f1 + self.tol and s2 > f2 + self.tol:
            if (prev_util > 8):
                self.stick += 1
            elif (s1 > s2):
                self.prev_action = self.opposite(last_opp_1)
            else:
                self.prev_action = self.opposite(last_opp_2)
        elif f1 > max(max(s1, s2), f2) + self.tol:
            if (follow_cross[1][0] < follow_cross[1][2]):
                # 1 is following 2! sit on 2
                self.prev_action = last_opp_2
        elif f2 > max(max(s1, s2), f1) + self.tol:
            if (follow_cross[2][0] < follow_cross[2][1]):
                # 2 is following 1! sit on 1
                self.prev_action = last_opp_1
        elif f1 > s1 + self.tol and f2 > s2 + self.tol and follow_cross[1][2] > follow_cross[1][0] and follow_cross[2][
                1] > follow_cross[2][0]:
            # probably following each other
            if f1 > f2:
                self.prev_action = last_opp_1
            else:
                self.prev_action = last_opp_2
        elif last_opp_1 == self.opposite(last_opp_2):
            # they are opposite!
            # carrot and stick
            self.carrot_stick = 8
            if (f1 > f2):
                # f1 is less sticky - so just sit on top of it and force to move :D
                # but want to force it to collaborate with me... idk im too lazy to impl this part
                self.prev_action = last_opp_1
                self.bias = self.calc_bias(1, last_opp_2)
            else:
                self.prev_action = last_opp_2
                self.bias = self.calc_bias(2, last_opp_1)

        return self.prev_action

    def update(self):
        self.t += 1

################### SUBMISSION #####################
agent_submission = E2Agent("E2A")
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
                E2Agent("Agent_1"),
                E2Agent("Agent_2"),
                E2Agent("Agent_3"),
                E2Agent("Agent_4")
            ]
        )
        arena.run()
