import random
import numpy as np
from uniform_policy import UniformPolicy
from agt_server.agents.base_agents.chicken_agent import ChickenAgent
import os


class QLearning(ChickenAgent):
    def __init__(self, name, num_possible_states, num_possible_actions, initial_state, learning_rate, discount_factor, exploration_rate, training_mode, save_path=None) -> None:
        self.num_possible_actions = num_possible_actions
        self.num_possible_states = num_possible_states
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.training_mode = training_mode
        self.save_path = save_path
        self.s = initial_state
        super().__init__(name)

    def setup(self):
        self.my_states = []
        self.training_policy = UniformPolicy(self.num_possible_actions)

        if self.save_path and os.path.isfile(self.save_path):
            with open(self.save_path, 'rb') as saved_q_table:
                self.q = np.load(saved_q_table)
                assert self.q.shape[0] == self.num_possible_states, "The Saved Q-Table has a different number of states than inputed, To train on the new states please delete the Saved Q-Table"
                assert self.q.shape[1] == self.num_possible_actions, "The number of possible actions in the saved file is different from the actual game, please delete and train again."
        else:
            # initialize Q to random [-1, 1]
            self.q = np.array([[random.uniform(-1, 1)
                                for _ in range(self.num_possible_actions)]
                               for _ in range(self.num_possible_states)])

        # begin with initial state and random action.
        self.a = self.training_policy.get_move(self.s)
        self.s_prime = None

    def choose_next_move(self, s_prime):
        # In the next round, your agent will be in state [s_prime]. What move will it play?
        # TODO: Fill in the exploration-exploitation algorithm, choosing your next action
        # If in training mode,
        #    - Randomly choose an action (with probability self.exploration_rate)
        #    - Choose the best action (with probability 1 - self.exploration_rate)
        # Otherwise
        #    - Always choose the best action because you are no longer training
        # Hint: np.argmax and self.training_policy.get_move() may be useful!
        if (self.training_mode and random.random() < self.exploration_rate):
            return self.training_policy.get_move(self.s)
        else:
            return np.argmax(self.q[s_prime])

    def get_action(self):
        return self.a

    def set_training_mode(self, training_mode):
        self.training_mode = training_mode

    def determine_state(self):
        # Determines the next state s_prime given the action histories and reward histories
        # Don't worry about implementing this for now, you will implement this later
        raise NotImplementedError

    def update_rule(self, reward):
        # TODO: fill in the Q-learning update algorithm, updating self.Q
        # Q(s, a) = Q(s, a) + α[r + γ max_{a'} Q(s', a') − Q(s, a)]
        # Hint: np.max and self.s_prime may be useful!
        self.q[self.s, self.a] += self.learning_rate * \
            (reward + self.discount_factor *
             np.max(self.q[self.s_prime]) - self.q[self.s, self.a])
        if self.save_path:
            with open(self.save_path, 'wb') as saved_q_table:
                np.save(saved_q_table, self.q)

    def update(self):
        self.s_prime = self.determine_state()
        my_last_util = self.get_last_util()
        self.update_rule(my_last_util)
        self.s = self.s_prime
        self.a = self.choose_next_move(self.s_prime)
        self.s_prime = None
