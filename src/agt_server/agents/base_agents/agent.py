import socket
import json
import uuid
from agt_server.agents.base_agents.game_report import GameReport
from agt_server.utils import extract_first_json


class Agent:
    def __init__(self, name=None, timestamp = None):
        self.name = name
        self.timestamp = timestamp
        self.client = None
        self.player_type = None
        self.game_report = GameReport()
        self.game_num = 1
        self.global_timeout_count = 0
        self.curr_opps = []

    def respond_to_request(self, key, value):
        data = self.client.recv(1024).decode()
        data = extract_first_json(data)
        
        if data:
            request = json.loads(data)
            if request['message'] == f'request_{key}':
                message = {
                    "message": f"provide_{key}",
                    f"{key}": value
                }
                self.client.send(json.dumps(message).encode())

    def setup(self):
        raise NotImplementedError

    def restart(self):
        self.game_report = GameReport()
        self.setup()
    
    def teardown(self): 
        # TODO: While the active competition is running we can't have this raising an Error but have it raise an error afterwards to be more robust 
        pass

    def get_device_id(self):
        return uuid.UUID(int=uuid.getnode()).hex[-12:]

    def connect(self, ip='localhost', port=1234):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip, port))
        try:
            self.name = str(self.name)
        except:
            raise Exception("Agent must have a Stringifiable Name")
        self.respond_to_request("device_id", self.get_device_id())
        self.respond_to_request("name", self.name)
        data = self.client.recv(1024).decode()
        data = extract_first_json(data)
        
        if data:
            response = json.loads(data)
            if response['message'] == 'provide_name':
                self.name = response['name']
                message = {
                    "message": "name_updated",
                }
                self.client.send(json.dumps(message).encode())
                print(f"My name is {self.name}")
        self.play()

    def get_action(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def play(self):
        raise NotImplementedError

    def close(self):
        self.client.close()
    
    def __str__(self):
        return self.name