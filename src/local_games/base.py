import signal


class LocalArena:
    def __init__(self, num_rounds, players, timeout, handin):
        self.num_rounds = num_rounds
        self.players = players
        self.timeout = timeout
        self.handin_mode = handin
        self.timeout_tolerance = 10
        self.game_reports = {}

    @staticmethod
    def timeout_handler(signum, frame):
        raise TimeoutError("Function execution timed out")

    def run_func_w_time(self, func, timeout, name, alt_ret=None):
        signal.signal(signal.SIGALRM, LocalArena.timeout_handler)
        signal.alarm(timeout)

        try:
            ret = func()
            signal.alarm(0)  # Cancel the timeout alarm
            if name in self.game_reports and 'timeout_count' in self.game_reports[name]:
                self.game_reports[name]['timeout_count'] = 0 
        except TimeoutError:
            if not self.handin_mode:
                print(f"{name} Timed Out")
            if alt_ret is not None:
                ret = alt_ret
            if name in self.game_reports:
                if 'timeout_count' in self.game_reports[name]:
                    self.game_reports[name]['timeout_count'] += 1
                if 'global_timeout_count' in self.game_reports[name]:
                    self.game_reports[name]['global_timeout_count'] += 1
            
        return ret

    def run_game(self):
        raise NotImplementedError
