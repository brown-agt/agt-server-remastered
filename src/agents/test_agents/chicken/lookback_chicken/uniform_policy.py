from i_fixed_policy import IFixedPolicy
import numpy as np


class UniformPolicy(IFixedPolicy):
    def __init__(self, action_state_sz) -> None:
        super().__init__()
        self.action_state_sz = action_state_sz

    def get_move(self, state):
        return np.random.randint(0, self.action_state_sz)
