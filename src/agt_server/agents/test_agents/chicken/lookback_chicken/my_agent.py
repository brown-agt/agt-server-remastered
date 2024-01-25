from q_learning import QLearning
from agt_server.local_games.chicken_arena import ChickenArena
from agt_server.agents.test_agents.chicken.basic_agent.my_agent import BasicAgent
import argparse

NUM_TRAINING_ITERATIONS = 20000
NUM_ITERATIONS_PER_PRINT = 1000


class LookBackChicken(QLearning):
    def __init__(self, name, num_possible_states, num_possible_actions, initial_state, learning_rate, discount_factor, exploration_rate, training_mode, save_path=None) -> None:
        super().__init__(name, num_possible_states, num_possible_actions, initial_state,
                         learning_rate, discount_factor, exploration_rate, training_mode, save_path)

    def determine_state(self):
        opp_action_hist = self.get_opp_action_history()
        last_action = opp_action_hist[-1]
        if (len(opp_action_hist) < 2):
            return last_action

        second_last_action = opp_action_hist[-2]
        return 2 * second_last_action + last_action


NUM_TRAINING_ITERATIONS = 20000
NUM_ITERATIONS_PER_PRINT = 1000
# this agent only uses 4 states
NUM_POSSIBLE_STATES = 4
# chicken has 2 possible actions (CONTINUE and SWERVE).
NUM_POSSIBLE_ACTIONS = 2
INITIAL_STATE = 0

LEARNING_RATE = 0.05
DISCOUNT_FACTOR = 0.90
EXPLORATION_RATE = 0.05

################### SUBMISSION #####################
agent_submission = LookBackChicken("LookBack", NUM_POSSIBLE_STATES, NUM_POSSIBLE_ACTIONS,
                                   INITIAL_STATE, LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, True, None)
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
    parser.add_argument('--train', type=bool, default=True,
                        help='Train the qtable (default: True)')
    parser.add_argument('--save_path', type=str, default=None,
                        help='Path to save the qtable (default: None)')
    args = parser.parse_args()

    # START SIMULATING THE GAME
    agent = LookBackChicken(args.agent_name, NUM_POSSIBLE_STATES, NUM_POSSIBLE_ACTIONS,
                            INITIAL_STATE, LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, args.train, args.save_path)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = ChickenArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                BasicAgent("Agent_1"),
                BasicAgent("Agent_2"),
                BasicAgent("Agent_3"),
                BasicAgent("Agent_4")
            ]
        )
        arena.run()
