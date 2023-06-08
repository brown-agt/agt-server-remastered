class IFixedPolicy(object):
    def get_move(self, state):
        raise NotImplementedError
