from agents.base_agents.agent import Agent
import json
import pandas as pd
import threading


class BOSIIAgent(Agent):
    def __init__(self, name=None):
        super().__init__(name)
        self.GOOD_MOOD, self.BAD_MOOD = 0, 1
        self.mood = None
        self.utils = {self.GOOD_MOOD:
                      [[(0, 0), (3, 7)],
                       [(7, 3), (0, 0)]],
                      self.BAD_MOOD:
                      [[(0, 3), (3, 0)],
                       [(7, 0), (0, 7)]]}
        cfile = open("../../../../configs/server_configs/bosii_config.json")
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
            self.game_history['opp_action_history'].append(
                resp['opp_action'])
            self.game_history['opp_utils_history'].append(
                resp['opp_utils'])
            self.game_history['mood_history'].append(
                resp['mood']
            )
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
                    self.mood = request['mood']
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

    def print_results(self):
        action_counts = [0, 0, 0]
        for action in self.game_history['my_action_history']:
            if action in [0, 1]:
                action_counts[action] += 1
            else:
                action_counts[2] += 1
        print(f"Game {self.game_num}:")
        if self.curr_opps: 
            if len(self.curr_opps) > 1: 
                and_str += ', and '
            print(f"I am currently playing against {', '.join(self.curr_opps[:-1]) + and_str + self.curr_opps[-1]}")
        print(
            f"{self.name} was COMPROMISING {action_counts[0]} times and was STUBBORN {action_counts[1]} times")
        if action_counts[2] > 0:
            print(f"{self.name} submitted {action_counts[2]} invalid moves")
        if self.global_timeout_count > 0:
            print(f"{self.name} timed out {self.global_timeout_count} times")
        total_util = sum(self.game_history['my_utils_history'])
        avg_util = total_util / len(self.game_history['my_utils_history'])

        print(
            f"{self.name} got a total utility of {total_util} and a average utility of {avg_util}")
        self.game_num += 1

    def get_action_history(self):
        return self.game_history['my_action_history']

    def get_util_history(self):
        return self.game_history['my_utils_history']

    def get_opp_action_history(self):
        return self.game_history['opp_action_history']

    def get_opp_util_history(self):
        return self.game_history['opp_utils_history']

    def get_mood_history(self):
        return self.game_history['mood_history']

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

    def get_last_mood(self):
        if len(self.game_history['mood_history']) > 0:
            return self.game_history['mood_history'][-1]

    def is_row_player(self):
        return self.player_type == "row_player"

    def get_mood(self):
        return self.mood

    def row_player_calculate_util(self, row_move, col_move):
        return self.utils[self.GOOD_MOOD][row_move][col_move][0]

    def col_player_calculate_util(self, row_move, col_move, mood):
        return self.utils[mood][row_move][col_move][1]

    def col_player_good_mood_prob(self):
        return 2/3
