import asyncio
import socket
import numpy as np
import math
import pandas as pd
import time
import json
from collections import defaultdict
from itertools import permutations, product
import argparse


class Server:
    def __init__(self, config_file, ip=None, port=None):
        cfile = open(config_file)
        server_config = json.load(cfile)
        self.n_players = 0

        if port != None:
            self.port = port
        else:
            self.port = 8080

        if ip != None:
            self.ip = ip
        else:
            hostname = socket.gethostname()
            self.ip = socket.gethostbyname(hostname)

        self.game_name = server_config['game_name']
        self.signup_time = server_config['signup_time']
        self.player_types = server_config['player_types']
        self.permission_map = server_config['permissions']
        self.type_configurations = server_config['type_configurations']
        self.players_per_game = server_config['num_players_per_game']
        self.num_rounds = server_config['num_rounds'] + 1
        self.save_results = server_config['save_results']
        self.save_path = server_config['save_path']
        self.display_results = server_config['display_results']
        self.kick_time = server_config['kick_time']
        self.send_results = server_config['send_results']
        self.check_dev_id = server_config['check_dev_id']
        self.invalid_move_penalty = server_config['invalid_move_penalty']
        self.timeout_tolerance = server_config['timeout_tolerance']
        self.df = None

        game_path = server_config['game_path']
        module_name, class_name = game_path.rsplit('.', 1)
        game_module = __import__(module_name, fromlist=[class_name])
        self.game = getattr(game_module, class_name)

        self.curr_round = 1
        self.player_data = defaultdict(lambda:
                                       {
                                           "name": None,
                                           "client": None,
                                           "device_id": None,
                                           "index": None, 
                                           "ingame": False, 
                                           "disconnected": False
                                       })
        self.result_table = None
        self.can_run_game = asyncio.Event()
        
    async def countdown(self):
        while self.signup_time > 0:
            print(f"{self.signup_time} seconds remaining")
            await asyncio.sleep(1)
            self.signup_time -= 1
        
        if self.players_per_game == 2: 
            self.result_table = np.zeros([self.n_players, self.n_players])
        else: 
            self.result_table = []

        message = {"message": "provide_game_name",
                   "game_name": self.game_name}
        for address in self.player_data:
            writer, reader = self.player_data[address]['client']
            try: 
                writer.write(json.dumps(message).encode())
                await writer.drain()
                data = await reader.read(1024)
                response = json.loads(data)
                assert response['message'] == "game_name_recieved"
            except Exception as e: 
                print(f"Failed to send game_name to {self.player_data[address]['name']}... Most likely disconnected")
                writer.close()
                await writer.wait_closed()
                self.player_data[address]['client'] = None
                self.player_data[address]['device_id'] = None
                self.player_data[address]['address'] = None
                self.player_data[address]['disconnected'] = True
                continue
        self.can_run_game.set() 
        
        return
    
    
    async def handle_client(self, reader, writer):
        address = writer.get_extra_info('peername')
        
        if self.signup_time <= 0:
            print(f"Client {address} has failed to connect [Sign Up Expired]")
            try: 
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=0.5)
            except asyncio.TimeoutError:
                pass
            return
        
        message = {"message": "request_device_id"}
        try: 
            writer.write(json.dumps(message).encode())
            await writer.drain()
            data = await reader.read(1024)
        except Exception as e: 
            print(f"Client {address} has failed to connect because {type(e).__name__}: {e}")
            try: 
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=0.5)
            except asyncio.TimeoutError:
                pass
            return
        
        # No response from client
        if not data:
            print(f"Client {address} has failed to connect [No Response]")
            writer.close()
            await writer.wait_closed()
            return
        try:
            response = json.loads(data)
        except:
            print(f"Client {address} has failed to connect [Invalid Response]")
            writer.close()
            await writer.wait_closed()
            return
        
        if response['message'] != "provide_device_id" or response['device_id'] == None:
            print(f"Client {address} has failed to connect [No Device ID Provided]")
            writer.close()
            await writer.wait_closed()
            return
        
        device_id = response['device_id']
        
        self.n_players += 1
        print(f"Accepted connection from {address} ({device_id})")
        
        # Check if device is already connected
        if self.check_dev_id:
            if device_id in [pd['device_id'] for pd in self.player_data.values()]:
                print(f"Client {address} ({device_id}) is already connected")
                writer.close()
                await writer.wait_closed()
                self.n_players -= 1
                return
        
        message = {"message": "request_name"}
        try: 
            writer.write(json.dumps(message).encode())
            await writer.drain()
            data = await reader.read(1024)
        except Exception as e: 
            print(f"Failed to send recieve name from {address} because {type(e).__name__}: {e}")
            writer.close()
            await writer.wait_closed()

        # No response from client
        if not data:
            print(f"Client {address} has disconnected unexpectedly")
            writer.close()
            await writer.wait_closed()
            self.n_players -= 1
            return
    
        try:
            response = json.loads(data)
        except:
            print(f"Client {address} has disconnected unexpectedly")
            print("Please check if their name is too long, the name can be at most 900 characters long")
            writer.close()
            await writer.wait_closed()
            self.n_players -= 1
            return

        if response['message'] != "provide_name" or response['name'] == None:
            print(f"Client {address} did not provide name")
            writer.close()
            await writer.wait_closed()
            self.n_players -= 1
            return

        # Add player to active list
        self.player_data[address]['client'] = (writer, reader)
        self.player_data[address]['device_id'] = device_id
        self.player_data[address]['index'] = self.n_players - 1
        self.player_data[address]['address'] = address

        response['name'] = response['name'].strip()
        counter = 0
        extension = ""
        while any([response['name'] + extension == data['name'] for data in self.player_data.values()]):
            extension = f" ({counter + 1})"
            counter += 1
        self.player_data[address]['name'] = response['name'] + extension
        message = {"message": "provide_name", "name": self.player_data[address]['name']}
        try: 
            writer.write(json.dumps(message).encode())
            await writer.drain()
            data = await reader.read(1024)
            response = json.loads(data)
            assert response['message'] == "name_updated"
        except Exception as e: 
            print(f"Client {address} has failed to connect because {type(e).__name__}: {e}")
            writer.close()
            await writer.wait_closed()
            self.player_data[address]['client'] = None
            self.player_data[address]['device_id'] = None
            self.player_data[address]['address'] = None
            self.player_data[address]['disconnected'] = True
            self.n_players -= 1
            return
        
        print(f"{self.player_data[address]['name']} has joined the game \n")
    
    async def run_server(self, host, port):
        self.signup_start_time = time.time()
        countdown_task = asyncio.create_task(self.countdown())
        gamerunning_task = asyncio.create_task(self.run_game())
        server = await asyncio.start_server(self.handle_client, host, port)

        async with server:
            try:
                await gamerunning_task
                await self.close()
            except asyncio.CancelledError:
                if not gamerunning_task.done():
                    gamerunning_task.cancel()
                await gamerunning_task
            finally:
                server.close()
                await server.wait_closed()
                if not countdown_task.done():
                    countdown_task.cancel()
                await asyncio.gather(countdown_task, return_exceptions=True)
                
            
    async def start(self):
        try:
            print(f'The server is hosted at {self.ip} and port {self.port}')
            await self.run_server(self.ip, self.port)
        except KeyboardInterrupt:
            pass
        return
    
    async def process_game_results(self, game_task, addresses):
        try:
            game_reports = await game_task
        except Exception as e:
            print(f"Error in game with {self.player_data[address]['name']} because {type(e).__name__}: {e}")
            for address in addresses:
                self.player_data[address]['disconnected'] = True
            return

        for address in game_reports:
            if game_reports[address]['disconnected']:
                print(f"Client {self.player_data[address]['name']}: {address} has disconnected unexpectedly")
                # writer, _ = self.player_data[address]['client']
                # print("Got the writer")
                # try: 
                #     writer.close()
                #     await asyncio.wait_for(writer.wait_closed(), timeout=0.5)
                # except asyncio.TimeoutError:
                #     continue
                # LOGGING: Delete this
                # print(f"Writer has finished closing", flush=True) 
                self.player_data[address]['client'] = None
                self.player_data[address]['device_id'] = None
                self.player_data[address]['address'] = None
                self.player_data[address]['disconnected'] = True
                self.n_players -= 1
            else:
                total_util = sum(game_reports[address]['util_history'])
                if self.players_per_game == 2: 
                    for opp_address in game_reports:
                        if address != opp_address:
                            self.result_table[self.player_data[address]['index'],
                                            self.player_data[opp_address]['index']] += total_util
                            
            if self.players_per_game > 2: 
                adds = []
                total_utils = []
                winner, ws = None, float("-inf")
                for address in game_reports: 
                    adds.append(address)
                    total_util = sum(game_reports[address]['util_history'])
                    total_utils.append(total_util)
                    if total_util > ws: 
                        winner = self.player_data[address]['name']
                        ws = total_util
                self.result_table.append(adds + total_utils + [winner])   
        for address in addresses: 
            self.player_data[address]["ingame"] = False

    async def run_game(self):
        await self.can_run_game.wait()
        print(f'I have {self.n_players} agents connected and I am starting the {self.game_name} game')
        
        game_tasks = []
        pairings = list(permutations(self.player_data, r=self.players_per_game))
        while pairings: 
            new_pairings = []
            for addresses in pairings: 
                if any([self.player_data[address]["disconnected"] for address in addresses]):
                    continue
                elif all([not self.player_data[address]["ingame"] for address in addresses]): 
                    for address in addresses: 
                        self.player_data[address]["ingame"] = True 
                    if self.type_configurations == "all":
                        type_configs = product(self.player_types, repeat=self.players_per_game)
                    else:
                        type_configs = self.type_configurations
                    for player_types in type_configs:
                        game_player_data = [self.player_data[address]
                                            for address in addresses]
                        if (any([pd['client'] == None for pd in game_player_data])):
                            continue
                        
                        game = self.game(self.num_rounds, game_player_data, player_types,
                                        self.permission_map, self.kick_time, self.game_name, self.invalid_move_penalty,
                                        self.timeout_tolerance)
                        game_task = asyncio.create_task(game.run_game())
                        result_processing_task = asyncio.create_task(self.process_game_results(game_task, addresses))
                        game_tasks.append(result_processing_task)  
                else: 
                    new_pairings.append(addresses)
                    
            pairings = new_pairings
            await asyncio.gather(*game_tasks, return_exceptions=True)
        
        if self.players_per_game == 2: 
            df = pd.DataFrame(self.result_table)
            agent_names = [pld['name'] for pld in self.player_data.values()]
            df.columns = agent_names
            df.index = agent_names
            means = []
            for i, pld in enumerate(self.player_data.values()):
                if pld['client'] == None:
                    self.result_table[i, :] = 0
                    self.result_table[:, i] = 0 
            
            for pld, d in zip(self.player_data.values(), self.result_table):
                if pld['client'] == None:
                    means.append(float('-inf'))
                elif self.n_players <= 1:
                    means.append(0)
                else:
                    means.append(sum(d) / (self.n_players - 1))

            df['Mean Points'] = means
            final_scores = [m / (self.num_rounds * math.factorial(self.players_per_game)) for m in means]
            df['Final Score'] = final_scores
            df = df.sort_values('Mean Points', ascending=False)
            df['Mean Points'] = np.where(df['Mean Points'] == float(
                '-inf'), 'Disconnected', df['Mean Points'])
            df['Final Score'] = np.where(df['Final Score'] == float(
                '-inf'), 'Disconnected', df['Final Score'])
        else: 
            extended_results = [
                [self.player_data[a]['name'], self.player_data[b]['name'], self.player_data[c]['name'], *rest] for 
                a, b, c, *rest in self.result_table
            ]
            df = pd.DataFrame(extended_results)
            df.columns = ['Agent 1', 'Agent 2', 'Agent 3',
                        'Agent 1 Score', 'Agent 2 Score', 'Agent 3 Score', 'Winner']
            print(f"Extended Results: \n {df}")

            total_util_dict = defaultdict(lambda: [0, 0])
            for p1, p2, p3, p1_util, p2_util, p3_util, _ in self.result_table:
                total_util_dict[p1][0] += p1_util
                total_util_dict[p2][0] += p2_util
                total_util_dict[p3][0] += p3_util
                total_util_dict[p1][1] += 1
                total_util_dict[p2][1] += 1
                total_util_dict[p3][1] += 1

            res_summary = []
            for key, value in total_util_dict.items():
                name = self.player_data[key]['name']
                if self.player_data[key]['client'] == None:
                    res_summary.append([name, float('-inf'), float('-inf')])
                elif value[1] > 0:
                    res_summary.append(
                        [name, value[0] / value[1], value[0] / (value[1] * self.num_rounds)])
                else:
                    res_summary.append([name, 0, 0])

            df = pd.DataFrame(res_summary)
            df.columns = ['Agent Name', 'Average Utility', 'Final Score']
            df = df.sort_values('Final Score', ascending=False)
            df['Average Utility'] = df['Average Utility'].replace(float('-inf'), 'Disconnected')
            df['Final Score'] = df['Final Score'].replace(float('-inf'), 'Disconnected')
        
        if self.save_results:
            timestamp = time.strftime("%b %d %Y %H:%M:%S")
            df.to_csv(f"{self.save_path}/{timestamp}.csv")
        self.df = df
        if self.display_results:
            print(df)
        return df

    async def close(self):
        message = {"message": "game_end",
                   "send_results": self.send_results,
                   "results": self.df.to_json()}
        if not self.send_results:
            message['results'] = "Please check in with your Lab TA for the results"

        for address in self.player_data:
            if self.player_data[address]['client']:
                writer, _ = self.player_data[address]['client']
                try: 
                    writer.write(json.dumps(message).encode())
                    await writer.drain()
                except Exception as e: 
                    print(f"Failed to send final results to {self.player_data[address]['name']} because {type(e).__name__}: {e}")
                    continue



async def main():
    parser = argparse.ArgumentParser(description='My Server')
    parser.add_argument('server_config', type=str,
                        help='Relative Path of the server config file starting from config/server_configs')
    parser.add_argument('--ip', type=str, help='IP address to bind the server to')
    parser.add_argument('--port', type=int, help='Port number to bind the server to')

    args = parser.parse_args()
    full_config = f"../../configs/server_configs/{args.server_config}"

    server = Server(full_config, args.ip, args.port)
    await server.start()

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Server ran in {end_time - start_time} seconds")
