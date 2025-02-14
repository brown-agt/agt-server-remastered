from agt_server.agents.base_agents.lemonade_agent import LemonadeAgent
from agt_server.local_games.lemonade_arena import LemonadeArena
import argparse
import random
import numpy as np

"""
Calculates the score obtained by a move given the opponents' moves

Params:
    me - an int mod 12, the move to score
    opp_1 - an int mod 12, opponent 1's move
    opp_2 - an int mod 12, opponent 2's move
Returns:
    an int - the score obtained by the given move
"""


def calc_score(me, opp_1, opp_2):
    if me == opp_1 and me == opp_2:
        return 8
    if me == opp_1 or me == opp_2:
        return 6

    shifted_1 = (opp_1 - me) % 12
    shifted_2 = (opp_2 - me) % 12
    bigger = max(shifted_1, shifted_2)
    smaller = min(shifted_1, shifted_2)
    return 12 - bigger + smaller


"""
Given the two opponents' moves, randomly picks from the optimal responses

Params:
    opp_1 - an int mod 12, opponent 1's move
    opp_2 - an int mod 12, opponent 2's move
Returns:
    an int mod 12 - a randomly chosen optimal response
"""


def best_move(opp_1, opp_2):
    max_score = 0
    for i in range(12):
        max_score = max(max_score, calc_score(i, opp_1, opp_2))

    optimal_moves = []
    for i in range(12):
        if calc_score(i, opp_1, opp_2) == max_score:
            optimal_moves.append(i)

    index = random.randrange(len(optimal_moves))
    return optimal_moves[index]

class TeamPlayer(LemonadeAgent):

    def setup(self):
        pass

    def get_action(self):
        try:
            if random.randint(0, 1) % 2 == 0:
                opp1 = self.get_opp1_action_history()
                opp2 = self.get_opp2_action_history()
            else:
                opp1 = self.get_opp2_action_history()
                opp2 = self.get_opp1_action_history()
            # stay far away from stable ones
            if opp1[-2] == opp1[-1] and (opp1[-1] - opp2[-1]) % 12 != 6:
                action = (opp1[-1] + 6) % 12
            elif opp2[-2] == opp2[-1] and (opp1[-1] - opp2[-1]) % 12 != 6:
                action = (opp2[-1] + 6) % 12
            else:
                # action = best_move(self.opponent_1_actions[-1], self.opponent_2_actions[-1])
                biased_flip = True if random.randint(0, 3) % 4 == 0 else False
                action = random.randint(0, 11) if biased_flip else self.get_action_history()[-1]
        except:
            action = random.randint(0, 11)
        return action

    def update(self):
        pass

################### SUBMISSION #####################
agent_submission = TeamPlayer("tp")
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
                TeamPlayer("Agent_1"),
                TeamPlayer("Agent_2"),
                TeamPlayer("Agent_3"),
                TeamPlayer("Agent_4")
            ]
        )
        arena.run()
