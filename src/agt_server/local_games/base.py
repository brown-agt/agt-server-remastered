import threading

class LocalArena:
    def __init__(self, num_rounds, players, timeout, handin):
        self.num_rounds = num_rounds
        self.players = players
        self.timeout = timeout
        self.handin_mode = handin
        self.timeout_tolerance = 10
        self.game_reports = {}

    def run_func_w_time(self, func, timeout, name, alt_ret=None):
        def target_wrapper():
            nonlocal ret
            try:
                ret = func()
                if name in self.game_reports and 'timeout_count' in self.game_reports[name]:
                    self.game_reports[name]['timeout_count'] = 0
            except Exception as e:
                print(f"Exception in thread running {name}: {e}")

        ret = alt_ret
        thread = threading.Thread(target=target_wrapper)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            # Handling the timeout scenario
            thread.join()  # Ensure the thread has finished
            if not self.handin_mode:
                print(f"{name} Timed Out")
            if name in self.game_reports:
                if 'timeout_count' in self.game_reports[name]:
                    self.game_reports[name]['timeout_count'] += 1
                if 'global_timeout_count' in self.game_reports[name]:
                    self.game_reports[name]['global_timeout_count'] += 1
        
        return ret

    def run_game(self):
        raise NotImplementedError
