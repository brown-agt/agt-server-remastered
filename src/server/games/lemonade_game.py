from games.game import Game
import socket
import json
import numpy as np


class LemonadeGame(Game):
    def __init__(self, num_rounds=1000, player_data=[], player_types=[], permissions_map={}, game_turn_timeout=1, game_name=None, invalid_move_penalty=0):
        super().__init__(num_rounds, player_data,
                         player_types, permissions_map, game_turn_timeout, game_name, invalid_move_penalty)
        for data in self.player_data:
            self.game_reports[data['address']] = {
                "action_history": [],
                "util_history": [],
                "disconnected": False
            }
        self.valid_actions = list(range(12))

    def calculate_utils(self, p1_action, p2_action, p3_action):
        utils = [0, 0, 0]
        if p1_action not in self.valid_actions and p2_action not in self.valid_actions and p3_action not in self.valid_actions:
            utils = [0, 0, 0]
        elif p1_action not in self.valid_actions and p2_action not in self.valid_actions:
            utils = [self.invalid_move_penalty, self.invalid_move_penalty, 24]
        elif p1_action not in self.valid_actions and p3_action not in self.valid_actions:
            utils = [self.invalid_move_penalty, 24, self.invalid_move_penalty]
        elif p2_action not in self.valid_actions and p3_action not in self.valid_actions:
            utils = [24, self.invalid_move_penalty, self.invalid_move_penalty]
        elif p1_action not in self.valid_actions:
            utils = [self.invalid_move_penalty, 12, 12]
        elif p2_action not in self.valid_actions:
            utils = [12, self.invalid_move_penalty, 12]
        elif p3_action not in self.valid_actions:
            utils = [12, 12, self.invalid_move_penalty]
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

    def simulate_round(self):
        p1 = self.player_data[0]['address']
        p2 = self.player_data[1]['address']
        p3 = self.player_data[2]['address']
        if self.game_reports[p1]['disconnected'] or self.game_reports[p2]['disconnected'] or self.game_reports[p3]['disconnected']:
            p1_util, p2_util, p3_util = 0, 0, 0
        else:
            p1_action = self.game_reports[p1]['action_history'][-1]
            p2_action = self.game_reports[p2]['action_history'][-1]
            p3_action = self.game_reports[p3]['action_history'][-1]
            p1_util, p2_util, p3_util = self.calculate_utils(
                p1_action, p2_action, p3_action)
        self.game_reports[p1]['util_history'].append(p1_util)
        self.game_reports[p2]['util_history'].append(p2_util)
        self.game_reports[p3]['util_history'].append(p3_util)

    def run_game(self):
        for round in range(self.num_rounds):
            for i in range(len(self.player_data)):
                data = self.player_data[i]
                player_type = self.player_types[i]
                client = data['client']
                message = {"message": "send_preround_data",
                           "player_type": player_type}

                if not self.game_reports[data['address']]['disconnected'] == True:
                    client.send(json.dumps(message).encode())
                    try:
                        resp = client.recv(1024).decode()
                        resp = json.loads(resp)
                        assert(resp['message'] == 'preround_data_recieved')
                    except socket.timeout:
                        continue
                    except:
                        self.game_reports[data['address']
                                          ]['disconnected'] = True

            for data in self.player_data:
                client = data['client']
                message = {"message": "request_action"}
                if not self.game_reports[data['address']]['disconnected'] == True:
                    client.send(json.dumps(message).encode())
                    try:
                        resp = client.recv(1024).decode()
                        if not resp:
                            self.game_reports[data['address']
                                              ]['disconnected'] = True
                            self.game_reports[data['address']
                                              ]['action_history'].append(-1)
                        else:
                            resp = json.loads(resp)
                            if resp and resp['message'] == 'provide_action':
                                self.game_reports[data['address']
                                                  ]['action_history'].append(resp['action'])
                    except socket.timeout:
                        print(f"{data['name']} has timed out")
                        self.game_reports[data['address']
                                          ]['action_history'].append(-1)
                    except:
                        self.game_reports[data['address']
                                          ]['disconnected'] = True
                        self.game_reports[data['address']
                                          ]['action_history'].append(-1)
            self.simulate_round()

            if round != self.num_rounds - 1:
                for i in range(len(self.player_data)):
                    data = self.player_data[i]
                    player_type = self.player_types[i]
                    opp1_data = self.player_data[(1 - i) % 3]
                    opp2_data = self.player_data[(1 - i) % 3]
                    client = data['client']

                    # EDIT THIS TO ADD PERMISSIONS
                    if 'all' in self.permissions_map[player_type] and self.permissions_map[player_type]['all']:
                        message = {"message": "prepare_next_round",
                                   "player_type": player_type,
                                   "permissions": ['all'],
                                   "my_action": self.game_reports[data['address']]['action_history'][-1],
                                   "my_utils": self.game_reports[data['address']]['util_history'][-1],
                                   "opp1_action":  self.game_reports[opp1_data['address']]['action_history'][-1],
                                   "opp1_utils": self.game_reports[opp1_data['address']]['util_history'][-1],
                                   "opp2_action":  self.game_reports[opp2_data['address']]['action_history'][-1],
                                   "opp2_utils": self.game_reports[opp2_data['address']]['util_history'][-1],
                                   }
                    else:
                        message = {"message": "prepare_next_round",
                                   "player_type": player_type,
                                   "permissions": [],
                                   }
                        if 'my_action' in self.permissions_map[player_type] and self.permissions_map[player_type]['my_action']:
                            message['my_action'] = self.game_reports[data['address']
                                                                     ]['action_history'][-1]
                            message['permissions'].append('my_action')
                        if 'my_utils' in self.permissions_map[player_type] and self.permissions_map[player_type]['my_utils']:
                            message['my_utils'] = self.game_reports[data['address']
                                                                    ]['util_history'][-1]
                            message['permissions'].append('my_utils')
                        if 'opp1_action' in self.permissions_map[player_type] and self.permissions_map[player_type]['opp1_action']:
                            message['opp1_action'] = self.game_reports[opp1_data['address']
                                                                       ]['action_history'][-1]
                            message['permissions'].append('opp1_action')
                        if 'opp1_utils' in self.permissions_map[player_type] and self.permissions_map[player_type]['opp1_utils']:
                            message['opp1_utils'] = self.game_reports[opp1_data['address']
                                                                      ]['util_history'][-1]
                            message['permissions'].append('opp1_utils')

                        if 'opp2_action' in self.permissions_map[player_type] and self.permissions_map[player_type]['opp2_action']:
                            message['opp2_action'] = self.game_reports[opp2_data['address']
                                                                       ]['action_history'][-1]
                            message['permissions'].append('opp2_action')
                        if 'opp2_utils' in self.permissions_map[player_type] and self.permissions_map[player_type]['opp2_utils']:
                            message['opp2_utils'] = self.game_reports[opp2_data['address']
                                                                      ]['util_history'][-1]
                            message['permissions'].append('opp2_utils')

                    if not self.game_reports[data['address']]['disconnected'] == True:
                        client.send(json.dumps(message).encode())
                        try:
                            resp = client.recv(1024).decode()
                            resp = json.loads(resp)
                            assert(resp['message'] == 'ready_next_round')
                        except socket.timeout:
                            continue
                        except:
                            self.game_reports[data['address']
                                              ]['disconnected'] = True

        message = {"message": "prepare_next_game"}
        for data in self.player_data:
            if not self.game_reports[data['address']]['disconnected'] == True:
                data['client'].send(json.dumps(message).encode())
                try:
                    resp = data['client'].recv(1024).decode()
                    resp = json.loads(resp)
                    assert(resp['message'] == 'ready_next_game')
                except:
                    self.game_reports[data['address']]['disconnected'] = True

        return self.game_reports
