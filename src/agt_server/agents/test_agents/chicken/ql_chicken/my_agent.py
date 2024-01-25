from q_learning import QLearning
from agt_server.local_games.chicken_arena import ChickenArena
from agt_server.agents.test_agents.chicken.mystery_agent.my_agent import MysteryAgent
import argparse

NUM_TRAINING_ITERATIONS = 20000
NUM_ITERATIONS_PER_PRINT = 1000


class QLChicken(QLearning):
    def __init__(self, name, num_possible_states, num_possible_actions, initial_state, learning_rate, discount_factor, exploration_rate, training_mode, save_path=None) -> None:
        super().__init__(name, num_possible_states, num_possible_actions, initial_state,
                         learning_rate, discount_factor, exploration_rate, training_mode, save_path)

    def determine_state(self):
        # Determines the next state s_prime given the action histories and reward histories
        # TODO: Fill out this function
        my_action_hist = self.get_action_history()
        opp_action_hist = self.get_opp_action_history()
        my_reward_hist = self.get_util_history()

        m = 1
        state = 0
        for action in opp_action_hist[-5:]:
            state += m * action
            m *= 2
        return state


NUM_TRAINING_ITERATIONS = 20000
NUM_ITERATIONS_PER_PRINT = 1000
# this agent only uses 32 states
NUM_POSSIBLE_STATES = 32
# chicken has 2 possible actions (CONTINUE and SWERVE).
NUM_POSSIBLE_ACTIONS = 2
INITIAL_STATE = 0

LEARNING_RATE = 0.05
DISCOUNT_FACTOR = 0.90
EXPLORATION_RATE = 0.05

################### SUBMISSION #####################
agent_submission = QLChicken("QL", NUM_POSSIBLE_STATES, NUM_POSSIBLE_ACTIONS,
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
    agent = QLChicken(args.agent_name, NUM_POSSIBLE_STATES, NUM_POSSIBLE_ACTIONS,
                      INITIAL_STATE, LEARNING_RATE, DISCOUNT_FACTOR, EXPLORATION_RATE, args.train, args.save_path)
    if args.join_server:
        agent.connect(ip=args.ip, port=args.port)
    else:
        arena = ChickenArena(
            num_rounds=1000,
            timeout=1,
            players=[
                agent,
                MysteryAgent("Agent_1"),
                MysteryAgent("Agent_2"),
                MysteryAgent("Agent_3"),
                MysteryAgent("Agent_4")
            ]
        )
        arena.run()
