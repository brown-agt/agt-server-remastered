import threading
import traceback
from datetime import datetime
import os
import json

class LocalArena:
    def __init__(self, num_rounds, players, timeout, handin, logging_path, save_path):
        self.num_rounds = num_rounds
        self.players = players
        self.timeout = timeout
        self.handin_mode = handin
        self.timeout_tolerance = 5
        self.game_reports = {}
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.logging_path = f"{logging_path}/{timestamp}_log.txt"
        self.shortcut_path = f"{logging_path}/shortcut.json"
        if self.handin_mode and not os.path.exists(self.shortcut_path):
            empty_dict = {}
            with open(self.shortcut_path, 'w') as file:
                json.dump(empty_dict, file)
        
        self.save_path = save_path

    def run_func_w_time(self, func, timeout, name, alt_ret=None):
        def target_wrapper():
            nonlocal ret
            try:
                ret = func()
            except Exception as e:
                stack_trace = traceback.format_exc()
                if self.handin_mode: 
                    self.game_reports[name]['disconnected'] = True
                    with open(self.logging_path, 'a') as file:
                        file.write(f"Exception in thread running {name}: {e}\nStack Trace:\n{stack_trace}\n")
                else: 
                    print(f"Exception in thread running {name}: {e}\nStack Trace:\n{stack_trace}")
                    

        ret = alt_ret
        thread = threading.Thread(target=target_wrapper)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            thread.join()
            if not self.handin_mode:
                print(f"{name} Timed Out")
            else:
                with open(self.logging_path, 'a') as file:
                    file.write(f"{name} Timed Out\n")
            
            if name in self.game_reports:
                if 'timeout_count' in self.game_reports[name]:
                    self.game_reports[name]['timeout_count'] += 1
                if 'global_timeout_count' in self.game_reports[name]:
                    self.game_reports[name]['global_timeout_count'] += 1
        
        return ret

    def run_game(self):
        raise NotImplementedError
