import time


class LocalArena:
    def __init__(self, num_rounds, players, timeout):
        self.timeout = timeout
        self.num_rounds = num_rounds
        self.players = players
        self.game_name = "Please give your game a name"
        self.game_reports = {}

    @staticmethod
    def run_func_w_time(func, timeout, name, alt_ret=None):
        start_time = time.time()
        ret = func()
        end_time = time.time()
        if end_time - start_time > timeout:
            print(f"{name} Timed Out")
            if alt_ret != None:
                ret = alt_ret
        return ret

    def run_game(self):
        raise NotImplementedError
