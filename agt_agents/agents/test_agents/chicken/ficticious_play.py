import argparse
import numpy as np
from agents.base_agents.chicken_agent import ChickenAgent
from agents.local_games.chicken_arena import ChickenArena


class FictitiousPlayAgent(ChickenAgent):
    def setup(self):
        self.SWERVE, self.CONTINUE = 0, 1
        self.actions = [self.SWERVE, self.CONTINUE]
        self.opp_action_history = []

        # NOTE: Changing this will only change your perception of the utility and will not
        #       change the actual utility used in the game
        self.utility = [[0, -1], [1, -5]]

    def get_action(self):
        dist = self.predict()
        best_move = self.optimize(dist)
        return self.actions[best_move]

    def update(self):
        """
        Updates opp action history to be a record of opponent moves
        """
        self.opp_action_history = self.get_opp_action_history()

    def predict(self):
        """
        Uses the opponent’s previous moves (self.opp_action_history) to generate and save a probability distribution
        over the opponent’s next move in (self.dist).
        """
        dist = np.zeros(len(self.actions))
        for a in self.opp_action_history:
            dist[a] += 1
        if sum(dist) == 0:
            return np.ones(len(self.actions))/len(self.actions)
        return dist/sum(dist)

    def optimize(self, dist):
        """
        Given the distribution over the opponent's next move (output of predict) and knowledge of the payoffs (self.utility),
        Return the best move according to Ficticious Play.
        """
        # TODO Calculate the expected payoff of each action and return the action with the highest payoff
        action_utils = np.zeros(len(self.actions))
        for i, a in enumerate(self.actions):
            # Calculate the payoff
            for j, a in enumerate(self.actions):
                action_utils[i] += dist[j]*self.utility[i][j]

        best_action = np.argmax(action_utils)
        return best_action


if __name__ == "__main__":
    ##### EDIT THIS #####
    ip = '192.168.1.16'
    port = 1234

    #### DO NOT TOUCH THIS #####
    parser = argparse.ArgumentParser(description='My Agent')
    parser.add_argument('agent_name', type=str, help='Name of the agent')
    parser.add_argument('--run_server', action='store_true',
                        help='Connects the agent to the server')

    args = parser.parse_args()

    agent = FictitiousPlayAgent(args.agent_name)
    if args.run_server:
        agent.connect(ip=ip, port=port)
    else:
        arena = ChickenArena(players=[
            agent,
            FictitiousPlayAgent("Agent_1"),
            FictitiousPlayAgent("Agent_2"),
            FictitiousPlayAgent("Agent_3"),
            FictitiousPlayAgent("Agent_4")])
        arena.run()
