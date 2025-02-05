import argparse
import numpy as np
from agt_server.agents.base_agents.rps_agent import RPSAgent
from agt_server.local_games.rps_arena import RPSArena
from agt_server.agents.test_agents.rps.ta_agent.my_agent import TAAgent


class FictitiousPlayAgent(RPSAgent):
    def setup(self):
        self.ROCK, self.PAPER, self.SCISSORS = 0, 1, 2
        self.actions = [self.ROCK, self.PAPER, self.SCISSORS]
        self.opp_action_history = []

    def get_action(self):
        dist = self.predict()
        best_move = self.optimize(dist)
        return self.actions[best_move]

    def update(self):
        """
        Updates opp action history to be a record of opponent moves
        Rock - 0, Scissors - 1, Paper - 2
        """
        self.opp_action_history = self.get_opp_action_history()

    def predict(self):
        """
        Uses the opponent’s previous moves (self.opp_action_history) to generate and save a probability distribution
        over the opponent’s next move in dist.
        """
        print(self.opp_action_history)
        dist = np.zeros(len(self.actions))
        for a in self.opp_action_history:
            dist[a] += 1
        if sum(dist) == 0:
            return np.ones(len(self.actions))/len(self.actions)
        return dist/sum(dist)

    def optimize(self, dist):
        """
        Given the distribution over the opponent's next move (output of predict) and knowledge of the payoffs (self.calculate_utils),
        Return the best move according to Ficticious Play.
        Please return one of [self.ROCK, self.PAPER, self.SCISSORS]
        """
        # TODO Calculate the expected payoff of each action and return the action with the highest payoff
        action_utils = np.zeros(len(self.actions))
        for i, a1 in enumerate(self.actions):
            # Calculate the payoff
            for j, a2 in enumerate(self.actions):
                action_utils[i] += dist[j]* self.calculate_utils(a1, a2)[0]

        best_action = np.argmax(action_utils)
        return best_action

agent_submission = FictitiousPlayAgent("FP")

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
        arena = RPSArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                TAAgent("TA_Agent_1"),
                TAAgent("TA_Agent_2"),
                TAAgent("TA_Agent_3"),
                TAAgent("TA_Agent_4")
            ]
        )
        arena.run()
