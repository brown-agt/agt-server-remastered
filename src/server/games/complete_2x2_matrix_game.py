from games.game import Game
import socket
import json


class Complete2by2MatrixGame(Game):
    def __init__(self, num_rounds=1000, player_data=[], player_types=[], permissions_map={}, game_kick_timeout=60, game_name=None, invalid_move_penalty=0, timeout_tolerance=10):
        super().__init__(num_rounds, player_data,
                         player_types, permissions_map, game_kick_timeout, game_name, invalid_move_penalty, timeout_tolerance)
        self.valid_actions = []
        self.utils = []

        for data in self.player_data:
            self.game_reports[data['address']] = {
                "action_history": [],
                "util_history": [],
                "timeout_count": 0,
                "global_timeout_count": 0,
                "disconnected": False,
                "disqualification_message": ""
            }

    def simulate_round(self):
        p1 = self.player_data[0]['address']
        p2 = self.player_data[1]['address']
        if self.game_reports[p1]['disconnected'] or self.game_reports[p2]['disconnected']:
            self.game_reports[p1]['util_history'].append(0)
            self.game_reports[p2]['util_history'].append(0)
        elif self.game_reports[p1]['action_history'][-1] not in self.valid_actions and \
                self.game_reports[p2]['action_history'][-1] not in self.valid_actions:
            self.game_reports[p1]['util_history'].append(0)
            self.game_reports[p2]['util_history'].append(0)
        elif self.game_reports[p1]['action_history'][-1] not in self.valid_actions:
            self.game_reports[p1]['util_history'].append(
                self.invalid_move_penalty)
            self.game_reports[p2]['util_history'].append(0)
        elif self.game_reports[p2]['action_history'][-1] not in self.valid_actions:
            self.game_reports[p1]['util_history'].append(0)
            self.game_reports[p2]['util_history'].append(
                self.invalid_move_penalty)
        else:
            self.game_reports[p1]['util_history'].append(self.utils[self.game_reports[p1]['action_history'][-1]]
                                                                   [self.game_reports[p2]['action_history'][-1]][0])
            self.game_reports[p2]['util_history'].append(self.utils[self.game_reports[p1]['action_history'][-1]]
                                                                   [self.game_reports[p2]['action_history'][-1]][1])

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
                    except:
                        self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent failed to confirm readyness for the round"
                        self.game_reports[data['address']
                                          ]['disconnected'] = True
            for data in self.player_data:
                client = data['client']
                message = {"message": "request_action"}
                if not self.game_reports[data['address']]['disconnected'] == True:
                    if self.game_reports[data['address']]['timeout_count'] < self.timeout_tolerance:
                        client.send(json.dumps(message).encode())
                        try:
                            resp = client.recv(1024).decode()
                            if not resp:
                                self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent sent a blank action response"
                                self.game_reports[data['address']
                                                  ]['disconnected'] = True
                                self.game_reports[data['address']
                                                  ]['action_history'].append(-1)
                                self.game_reports[data['address']
                                              ]['timeout_count'] = 0
                            else:
                                resp = json.loads(resp)
                                if resp and resp['message'] == 'provide_action':
                                    if resp['timeout']: 
                                        print(f"{data['name']} has timed out")
                                        self.game_reports[data['address']
                                              ]['action_history'].append(-1)
                                        self.game_reports[data['address']
                                                        ]['timeout_count'] += 1
                                        self.game_reports[data['address']
                                                        ]['global_timeout_count'] += 1
                                    else: 
                                        self.game_reports[data['address']
                                                      ]['action_history'].append(resp['action'])
                                        self.game_reports[data['address']
                                              ]['timeout_count'] = 0
                        except socket.timeout:
                            self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent has timed out past server limits"
                            self.game_reports[data['address']
                                              ]['disconnected'] = True
                            self.game_reports[data['address']
                                              ]['action_history'].append(-1)
                        except Exception as e:
                            self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent had a socket error. {type(e).__name__}: {e}"
                            self.game_reports[data['address']
                                              ]['disconnected'] = True
                            self.game_reports[data['address']
                                              ]['action_history'].append(-1)
                    else:
                        self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent timed out {self.timeout_tolerance} times in a row"
                        self.game_reports[data['address']
                                          ]['disconnected'] = True
                        self.game_reports[data['address']
                                          ]['action_history'].append(-1)
            self.simulate_round()

            if round != self.num_rounds - 1:
                for i in range(len(self.player_data)):
                    data = self.player_data[i]
                    player_type = self.player_types[i]
                    opp_data = self.player_data[1 - i]
                    client = data['client']
                    
                    # EDIT THIS TO ADD PERMISSIONS
                    if 'all' in self.permissions_map[player_type] and self.permissions_map[player_type]['all']:
                        message = {"message": "prepare_next_round",
                                   "player_type": player_type,
                                   "permissions": ['all'],
                                   "my_action": self.game_reports[data['address']]['action_history'][-1],
                                   "my_utils": self.game_reports[data['address']]['util_history'][-1],
                                   "opp_action":  self.game_reports[opp_data['address']]['action_history'][-1],
                                   "opp_utils": self.game_reports[opp_data['address']]['util_history'][-1],
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
                        if 'opp_action' in self.permissions_map[player_type] and self.permissions_map[player_type]['opp_action']:
                            message['opp_action'] = self.game_reports[opp_data['address']
                                                                      ]['action_history'][-1]
                            message['permissions'].append('opp_action')
                        if 'opp_utils' in self.permissions_map[player_type] and self.permissions_map[player_type]['opp_utils']:
                            message['opp_utils'] = self.game_reports[opp_data['address']
                                                                     ]['util_history'][-1]
                            message['permissions'].append('opp_utils')
                    message['global_timeout_count'] = self.game_reports[data['address']
                                                                        ]['global_timeout_count']
                    
                    if not self.game_reports[data['address']]['disconnected'] == True:
                        client.send(json.dumps(message).encode())
                        try:
                            resp = client.recv(1024).decode()
                            resp = json.loads(resp)
                            assert resp['message'] == 'ready_next_round', "Agent was not ready for the next round"
                        except socket.timeout:
                            continue
                        except Exception as e:
                            self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent was not ready for the next_round. {type(e).__name__}: {e}"
                            self.game_reports[data['address']
                                              ]['disconnected'] = True
                    else:
                        message = {"message": "disqualified",
                                   "disqualification_message": self.game_reports[data['address']]['disqualification_message']}
                        try:
                            client.send(json.dumps(message).encode())
                        except:
                            continue

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
