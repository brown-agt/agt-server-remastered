from games.game import Game
import asyncio
import json
import numpy as np
import logging

class SuppressSocketSendError(logging.Filter):
    def filter(self, record):
        return "socket.send() raised exception" not in record.getMessage()

logger = logging.getLogger('asyncio')
logger.addFilter(SuppressSocketSendError())

class BOSIIGame(Game):
    def __init__(self, num_rounds=1000, player_data=[], player_types=[], permissions_map={}, game_kick_timeout=60, game_name=None, invalid_move_penalty=0, timeout_tolerance=10):
        super().__init__(num_rounds, player_data,
                         player_types, permissions_map, game_kick_timeout, game_name, invalid_move_penalty, timeout_tolerance)
        self.GOOD_MOOD, self.BAD_MOOD = 0, 1
        for data in self.player_data:
            self.game_reports[data['address']] = {
                "action_history": [],
                "util_history": [],
                "mood_history": [],
                "timeout_count": 0,
                "global_timeout_count": 0,
                "disconnected": False,
                "disqualification_message": ""
            }
        self.valid_actions = [0, 1]
        self.utils = {self.GOOD_MOOD:
                      [[(0, 0), (3, 7)],
                       [(7, 3), (0, 0)]],
                      self.BAD_MOOD:
                      [[(0, 3), (3, 0)],
                       [(7, 0), (0, 7)]]}

    def simulate_round(self, cp_mood):
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
            self.game_reports[p1]['util_history'].append(self.utils[cp_mood][self.game_reports[p1]['action_history'][-1]]
                                                                   [self.game_reports[p2]['action_history'][-1]][0])
            self.game_reports[p2]['util_history'].append(self.utils[cp_mood][self.game_reports[p1]['action_history'][-1]]
                                                                   [self.game_reports[p2]['action_history'][-1]][1])

    async def run_game(self):
        for round in range(self.num_rounds):
            mood = np.random.choice(
                [self.GOOD_MOOD, self.BAD_MOOD], p=[2/3, 1/3])
            for i in range(len(self.player_data)):
                data = self.player_data[i]
                player_type = self.player_types[i]
                writer, reader = data['client']
                message = {"message": "send_preround_data",
                           "player_type": player_type,
                           "mood": None}
                if player_type == "column_player":
                    message['mood'] = int(mood)

                if not self.game_reports[data['address']]['disconnected'] == True:
                    try:
                        # # LOGGING: Delete this
                        # print(f"Asking if {data['name']} is ready for preround data", flush=True)
                        writer.write(json.dumps(message).encode())
                        await writer.drain()
                        resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                        resp = json.loads(resp)
                        assert resp['message'] == 'preround_data_recieved', f"{data['name']} did not recieve preround_data"
                        # # LOGGING: Delete this
                        # print(f"{data['name']} recieved preround data", flush=True)
                    except asyncio.TimeoutError:
                        self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent has timed out past server limits"
                        self.game_reports[data['address']
                                          ]['disconnected'] = True
                    except Exception as e:
                        self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent failed to confirm readyness for the round. {type(e).__name__}: {e}"
                        self.game_reports[data['address']
                                          ]['disconnected'] = True

            for data in self.player_data:
                writer, reader = data['client']
                message = {"message": "request_action"}
                if not self.game_reports[data['address']]['disconnected'] == True:
                    if self.game_reports[data['address']]['timeout_count'] < self.timeout_tolerance:
                        try:
                            # # LOGGING: Delete this
                            # print(f"Asking {data['name']} for an action", flush=True)
                            writer.write(json.dumps(message).encode())
                            await writer.drain()
                            resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                            if not resp:
                                # # LOGGING: Delete this
                                # print(f"{data['name']} gave no response", flush=True)
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
                                        print(f"{data['name']} has timed out", flush=True)
                                        self.game_reports[data['address']
                                              ]['action_history'].append(-1)
                                        self.game_reports[data['address']
                                                        ]['timeout_count'] += 1
                                        self.game_reports[data['address']
                                                        ]['global_timeout_count'] += 1
                                    else: 
                                        # # LOGGING: Delete this
                                        # print(f"{data['name']} sucessfully gave action {resp['action']}", flush=True)   
                                        self.game_reports[data['address']
                                                      ]['action_history'].append(resp['action'])
                                        self.game_reports[data['address']
                                              ]['timeout_count'] = 0
                        except asyncio.TimeoutError:
                            # # LOGGING: Delete this
                            # print(f"{data['name']} has timed out", flush=True)  
                            self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent has timed out past server limits"
                            self.game_reports[data['address']
                                              ]['disconnected'] = True
                            self.game_reports[data['address']
                                              ]['action_history'].append(-1)
                        except Exception as e:
                            # # LOGGING: Delete this
                            # print(f"{data['name']} has other error", flush=True)  
                            self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent had a socket error. {type(e).__name__}: {e}"
                            self.game_reports[data['address']
                                              ]['disconnected'] = True
                            self.game_reports[data['address']
                                              ]['action_history'].append(-1)
                        self.game_reports[data['address']
                                      ]['mood_history'].append(int(mood))
                    else:
                        # # LOGGING: Delete this
                        # print(f"{data['name']} has timed out too much", flush=True)  
                        self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent timed out {self.timeout_tolerance} times in a row"
                        self.game_reports[data['address']
                                          ]['disconnected'] = True
                        self.game_reports[data['address']
                                          ]['action_history'].append(-1)
                        self.game_reports[data['address']
                                      ]['mood_history'].append(int(mood))
                         
            self.simulate_round(mood)

            if round != self.num_rounds - 1:
                # # LOGGING: Delete this
                # print(f"Starting Round", flush=True)
                for i in range(len(self.player_data)):
                    data = self.player_data[i]
                    player_type = self.player_types[i]
                    opp_data = self.player_data[1 - i]
                    writer, reader = data['client']
                    
                    # # LOGGING: Delete this
                    # print(f"Preparing message for {data['name']}", flush=True)

                    # EDIT THIS TO ADD PERMISSIONS
                    if 'all' in self.permissions_map[player_type] and self.permissions_map[player_type]['all']:

                        message = {"message": "prepare_next_round",
                                   "player_type": player_type,
                                   "permissions": ['all'],
                                   "opp_names": [opp_data['name']],
                                   "my_action": self.game_reports[data['address']]['action_history'][-1],
                                   "my_utils": self.game_reports[data['address']]['util_history'][-1],
                                   "opp_action":  self.game_reports[opp_data['address']]['action_history'][-1],
                                   "opp_utils": self.game_reports[opp_data['address']]['util_history'][-1],
                                   "mood": self.game_reports[data['address']]['mood_history'][-1]
                                   }
                    else:
                        message = {"message": "prepare_next_round",
                                   "player_type": player_type,
                                   "opp_names": [opp_data['name']],
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
                        if 'mood' in self.permissions_map[player_type] and self.permissions_map[player_type]['mood']:
                            message['mood'] = self.game_reports[data['address']
                                                                ]['mood_history'][-1]
                            message['permissions'].append(
                                'mood')
                    message['global_timeout_count'] = self.game_reports[data['address']
                                                                        ]['global_timeout_count']
                    
                    
                            
                    if not self.game_reports[data['address']]['disconnected'] == True:
                        try:
                            # # LOGGING: Delete this
                            # print(f"Asking if {data['name']} is ready", flush=True)
                            writer.write(json.dumps(message).encode())
                            await writer.drain()
                            resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                            resp = json.loads(resp)
                            assert resp['message'] == 'ready_next_round', f"{data['name']} was not ready for the next round"
                            # # LOGGING: Delete this
                            # print(f"{data['name']} is confirmed ready", flush=True)
                        except asyncio.TimeoutError:
                            self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent has timed out past server limits"
                            self.game_reports[data['address']
                                              ]['disconnected'] = True
                        except Exception as e:
                            self.game_reports[data['address']
                                          ]['disqualification_message'] = f"{data['name']} Disqualified: Agent was not ready for the next_round. {type(e).__name__}: {e}"
                            self.game_reports[data['address']
                                              ]['disconnected'] = True
                    else:
                        message = {"message": "disqualified",
                                   "disqualification_message": self.game_reports[data['address']]['disqualification_message']}
                        try:
                            # # LOGGING: Delete this
                            # print(f"Telling {data['name']} is disqualified", flush=True)  
                            writer.write(json.dumps(message).encode())
                            await writer.drain()
                        except Exception as e:
                            # # LOGGING: Delete this
                            # print(f"{data['name']} failed to recieve message, {type(e).__name__}: {e}", flush=True)  
                            continue

        message = {"message": "prepare_next_game"}
        for data in self.player_data:
            if not self.game_reports[data['address']]['disconnected'] == True:
                try:
                    writer, reader = data['client']
                    # # LOGGING: Delete this
                    # print(f"Telling {data['name']} to prepare next game", flush=True)  
                    writer.write(json.dumps(message).encode())
                    await writer.drain()
                    resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                    resp = json.loads(resp)
                    assert resp['message'] == 'ready_next_game', f"{data['name']} was not prepared for next game"
                    # # LOGGING: Delete this
                    # print(f"{data['name']} was prepared for the next game", flush=True)  
                except asyncio.TimeoutError:
                    self.game_reports[data['address']
                                    ]['disqualification_message'] = f"{data['name']} Disqualified: Agent has timed out past server limits"
                    self.game_reports[data['address']
                                        ]['disconnected'] = True
                except Exception as e:
                    self.game_reports[data['address']
                                    ]['disqualification_message'] = f"{data['name']} Disqualified: Agent was not ready for the next game. {type(e).__name__}: {e}"
                    self.game_reports[data['address']
                                        ]['disconnected'] = True
        return self.game_reports
