import argparse
import numpy as np
from agt_server.agents.base_agents.bosii_agent import BOSIIAgent
from agt_server.local_games.bosii_arena import BOSIIArena


class FictitiousPlayAgent(BOSIIAgent):
    def setup(self):
        self.COMPROMISE, self.STUBBORN = 0, 1
        self.GOOD_MOOD, self.BAD_MOOD = 0, 1
        self.actions = [self.COMPROMISE, self.STUBBORN]
        self.opp_action_history = []
        self.mood_history = []

    def get_action(self):
        dist_good, dist_bad = self.predict()
        best_move = self.optimize(dist_good, dist_bad)
        return self.actions[best_move]

    def update(self):
        """
        Updates opp action history to be a record of opponent moves
        Updates mood history to be a record of the column player's historical moods
        """
        self.opp_action_history = self.get_opp_action_history()
        self.mood_history = self.get_mood_history()

    def predict(self):
        """
        Uses the opponent’s previous moves (self.opp_action_history) to generate and save a probability distribution
        over the opponent’s next move in (self.dist).
        """
        dist_good = np.zeros(len(self.actions))
        dist_bad = np.zeros(len(self.actions))
        for a, mood in zip(self.opp_action_history, self.mood_history):
            if mood == self.GOOD_MOOD:
                dist_good[a] += 1
            elif mood == self.BAD_MOOD:
                dist_bad[a] += 1
        if sum(dist_good) == 0:
            dist_goodp = np.ones(len(self.actions))/len(self.actions)
        else:
            dist_goodp = dist_good / sum(dist_good)

        if sum(dist_bad) == 0:
            dist_badp = np.ones(len(self.actions))/len(self.actions)
        else:
            dist_badp = dist_bad / sum(dist_bad)
        return dist_goodp, dist_badp

    def optimize(self, dist_good, dist_bad):
        """
        Given the distribution over the opponent's next move (output of predict) and knowledge of the payoffs (self.utility),
        Return the best move according to Ficticious Play.
        Please return one of [self.COMPROMISE, self.STUBBORN]
        """
        # TODO Calculate the expected payoff of each action and return the action with the highest payoff
        action_utils = np.zeros(len(self.actions))
        if self.is_row_player():
            for i, a in enumerate(self.actions):
                # Calculate the payoff
                for j, a in enumerate(self.actions):
                    action_utils[i] += self.col_player_good_mood_prob() * \
                        dist_good[j] * self.row_player_calculate_util(i, j)
                    action_utils[i] += (1 - self.col_player_good_mood_prob()) * \
                        dist_bad[j] * self.row_player_calculate_util(i, j)
        else:
            for i, a in enumerate(self.actions):
                # Calculate the payoff
                for j, a in enumerate(self.actions):
                    if self.get_mood() == self.GOOD_MOOD:
                        action_utils[i] += dist_good[j] * \
                            self.col_player_calculate_util(i, j, self.get_mood())
                    elif self.get_mood() == self.BAD_MOOD:
                        action_utils[i] += dist_bad[j] * \
                            self.col_player_calculate_util(i, j, self.get_mood())

        best_action = np.argmax(action_utils)
        return best_action

################### SUBMISSION #####################
agent_submission = FictitiousPlayAgent("Ficticious Play")
####################################################

if __name__ == "__main__":
    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--join_server', action='store_true',
                        help='Connects the agent to the server')
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help='IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port number (default: 8080)')

    args = parser.parse_args()

    agent = FictitiousPlayAgent(args.agent_name)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = BOSIIArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                FictitiousPlayAgent("Agent_1"),
                FictitiousPlayAgent("Agent_2"),
                FictitiousPlayAgent("Agent_3"),
                FictitiousPlayAgent("Agent_4")
            ]
        )
        arena.run()
