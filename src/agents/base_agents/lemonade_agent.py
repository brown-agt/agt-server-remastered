from agents.base_agents.agent import Agent
import json
import pandas as pd
import threading


class LemonadeAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name)
        self.valid_actions = list(range(12))
        cfile = open("../../../../configs/server_configs/lemonade_config.json")
        server_config = json.load(cfile)
        self.response_time = server_config['response_time']

    def timeout_handler(self):
        print(f"{self.name} has timed out")
        self.timeout = True

    def handle_permissions(self, resp):
        self.player_type = resp['player_type']
        if 'all' in resp['permissions']:
            self.game_history['my_action_history'].append(
                resp['my_action'])
            self.game_history['my_utils_history'].append(
                resp['my_utils'])
            self.game_history['opp1_action_history'].append(
                resp['opp1_action'])
            self.game_history['opp1_utils_history'].append(
                resp['opp1_utils'])
            self.game_history['opp2_action_history'].append(
                resp['opp2_action'])
            self.game_history['opp2_utils_history'].append(
                resp['opp2_utils'])
        else:
            for perm in resp['permissions']:
                self.game_history[f'{perm}_history'].append(
                    resp[perm])

    def handle_postround_data(self, resp):
        self.global_timeout_count = resp['global_timeout_count']
        self.curr_opps = resp['opp_names']
        self.handle_permissions(resp)

    def play(self):
        data = self.client.recv(1024).decode()
        if data:
            resp = json.loads(data)
            if resp['message'] == 'provide_game_name':
                print(f"We are playing {resp['game_name']}")
                message = {
                    "message": "game_name_recieved",
                }
                self.client.send(json.dumps(message).encode())
                self.restart()
        while True:
            data = self.client.recv(10000).decode()
            if data:
                request = json.loads(data)
                if request['message'] == 'send_preround_data':
                    self.player_type = request['player_type']
                    message = {"message": "preround_data_recieved"}
                    self.client.send(json.dumps(message).encode())
                    continue
                elif request['message'] == 'request_action':
                    self.timeout = False
                    try:
                        timer = threading.Timer(self.response_time, self.timeout_handler)
                        timer.start()
                        action = self.get_action()
                    finally:
                        if self.timeout: 
                            action = -1
                        timer.cancel()
                    
                    try:
                        action = int(action)
                        message = {
                            "message": "provide_action",
                            "action": action, 
                            "timeout": self.timeout
                        }
                        json_m = json.dumps(message).encode()
                        self.client.send(json_m)
                    except:
                        print("Warning: Get Action must return an Integer")
                        message = {
                            "message": "provide_action",
                            "action": -1, 
                            "timeout": self.timeout
                        }
                        json_m = json.dumps(message).encode()
                        self.client.send(json_m)
                elif request['message'] == 'game_end':
                    if request['send_results']:
                        try: 
                            df = pd.read_json(request['results'])
                            if df is not None:
                                print(df)
                        except: 
                            print("Results too large :(. Please check in with your Lab TA for the results")
                    else:
                        print(request['results'])
                    self.close()
                    break

            data = self.client.recv(1024).decode()
            if data:
                resp = json.loads(data)
                if resp['message'] == 'prepare_next_game':
                    self.print_results()
                    self.restart()
                    message = {"message": "ready_next_game"}
                    self.client.send(json.dumps(message).encode())
                elif resp['message'] == 'prepare_next_round':
                    self.handle_postround_data(resp)
                    self.update()
                    message = {"message": "ready_next_round"}
                    self.client.send(json.dumps(message).encode())
                elif resp['message'] == 'disqualified':
                    if resp['disqualification_message']:
                        print(resp['disqualification_message'])
                    self.close()
                    break

    def print_results(self):
        action_counts = [0 for _ in range(len(self.valid_actions) + 1)]
        for action in self.game_history['my_action_history']:
            if action in self.valid_actions:
                action_counts[action] += 1
            else:
                action_counts[len(self.valid_actions)] += 1
        print_smt = f"{self.name} set up their Lemonade Stand at"
        for i in range(len(self.valid_actions) - 1):
            print_smt += f" Location {i} {action_counts[i]} times,"
        print_smt += f" and Location {len(self.valid_actions) - 1} {action_counts[len(self.valid_actions) - 1]} times."
        print(f"Game {self.game_num}:")
        if self.curr_opps: 
            if len(self.curr_opps) > 1: 
                and_str += ', and '
            print(f"I am currently playing against {', '.join(self.curr_opps[:-1]) + and_str + self.curr_opps[-1]}")
        print(print_smt)
        if action_counts[len(self.valid_actions)] > 0:
            print(
                f"{self.name} submitted {action_counts[len(self.valid_actions)]} invalid moves")

        if self.global_timeout_count > 0:
            print(f"{self.name} timed out {self.global_timeout_count} times")

        total_util = sum(self.game_history['my_utils_history'])

        avg_util = total_util / \
            len(self.game_history['my_utils_history'])
        print(
            f"{self.name} got a total utility of {total_util} and a average utility of {avg_util}")
        self.game_num += 1

    def get_action_history(self):
        return self.game_history['my_action_history']

    def get_util_history(self):
        return self.game_history['my_utils_history']

    def get_opp1_action_history(self):
        return self.game_history['opp1_action_history']

    def get_opp1_util_history(self):
        return self.game_history['opp1_utils_history']

    def get_opp2_action_history(self):
        return self.game_history['opp2_action_history']

    def get_opp2_util_history(self):
        return self.game_history['opp2_utils_history']

    def get_last_action(self):
        if len(self.game_history['my_action_history']) > 0:
            return self.game_history['my_action_history'][-1]

    def get_last_util(self):
        if len(self.game_history['my_utils_history']) > 0:
            return self.game_history['my_utils_history'][-1]

    def get_opp1_last_action(self):
        if len(self.game_history['opp1_action_history']) > 0:
            return self.game_history['opp1_action_history'][-1]

    def get_opp1_last_util(self):
        if len(self.game_history['opp1_utils_history']) > 0:
            return self.game_history['opp1_utils_history'][-1]

    def get_opp2_last_action(self):
        if len(self.game_history['opp2_action_history']) > 0:
            return self.game_history['opp1_action_history'][-1]

    def get_opp2_last_util(self):
        if len(self.game_history['opp2_utils_history']) > 0:
            return self.game_history['opp1_utils_history'][-1]

    def calculate_utility(self, p1_action, p2_action, p3_action):
        utils = [0, 0, 0]
        if p1_action not in self.valid_actions and p2_action not in self.valid_actions and p3_action not in self.valid_actions:
            utils = [0, 0, 0]
        elif p1_action not in self.valid_actions and p2_action not in self.valid_actions:
            utils = [0, 0, 24]
        elif p1_action not in self.valid_actions and p3_action not in self.valid_actions:
            utils = [0, 24, 0]
        elif p2_action not in self.valid_actions and p3_action not in self.valid_actions:
            utils = [24, 0, 0]
        elif p1_action not in self.valid_actions:
            utils = [0, 12, 12]
        elif p2_action not in self.valid_actions:
            utils = [12, 0, 12]
        elif p3_action not in self.valid_actions:
            utils = [12, 12, 0]
        elif p1_action == p2_action and p2_action == p3_action:
            utils = [8, 8, 8]
        elif p1_action == p2_action:
            utils = [6, 6, 12]
        elif p1_action == p3_action:
            utils = [6, 12, 6]
        elif p2_action == p3_action:
            utils = [12, 6, 6]
        else:
            actions = [p1_action, p2_action, p3_action]
            sorted_actions = sorted(actions)
            index_map = {action: index for index,
                         action in enumerate(actions)}
            sorted_indices = [index_map[action]
                              for action in sorted_actions]
            u1 = sorted_actions[1] - sorted_actions[0]
            u2 = sorted_actions[2] - sorted_actions[1]
            u3 = 12 + sorted_actions[0] - sorted_actions[2]
            utils[sorted_indices[0]] = u1 + u3
            utils[sorted_indices[1]] = u1 + u2
            utils[sorted_indices[2]] = u2 + u3
        return utils
