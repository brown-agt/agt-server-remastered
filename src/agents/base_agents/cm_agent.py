from agents.base_agents.agent import Agent
import json
import pandas as pd
import threading


class CompleteMatrixAgent(Agent):
    def calculate_utils(self, p1_action, p2_action):
        if p1_action not in self.valid_actions and p2_action not in self.valid_actions:
            utils = [0, 0]
        elif p1_action not in self.valid_actions:
            utils = [self.invalid_move_penalty, 0]
        elif p2_action not in self.valid_actions:
            utils = [0, self.invalid_move_penalty]
        else:
            utils = [self.utils[p1_action][p2_action][0],
                     self.utils[p1_action][p2_action][1]]
        return utils

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
            self.game_history['opp_action_history'].append(
                resp['opp_action'])
            self.game_history['opp_utils_history'].append(
                resp['opp_utils'])
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
                            "timeout":self.timeout
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
                            print("Results too large. Please check in with your Lab TA for the results")
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

    def get_action_history(self):
        return self.game_history['my_action_history']

    def get_util_history(self):
        return self.game_history['my_utils_history']

    def get_opp_action_history(self):
        return self.game_history['opp_action_history']

    def get_opp_util_history(self):
        return self.game_history['opp_utils_history']

    def get_last_action(self):
        if len(self.game_history['my_action_history']) > 0:
            return self.game_history['my_action_history'][-1]

    def get_last_util(self):
        if len(self.game_history['my_utils_history']) > 0:
            return self.game_history['my_utils_history'][-1]

    def get_opp_last_action(self):
        if len(self.game_history['opp_action_history']) > 0:
            return self.game_history['opp_action_history'][-1]

    def get_opp_last_util(self):
        if len(self.game_history['opp_utils_history']) > 0:
            return self.game_history['opp_utils_history'][-1]
