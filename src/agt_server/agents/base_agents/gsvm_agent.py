import json
import random
import numpy as np
import pkg_resources
import threading
from agt_server.agents.base_agents.agent import Agent
from agt_server.agents.base_agents.game_report import GameReport
from agt_server.utils import extract_first_json
import pandas as pd

class GSVM9Agent(Agent):
    def __init__(self, name=None, timestamp=None):
        super().__init__(name, timestamp)

        config_path = pkg_resources.resource_filename('agt_server', 'configs/server_configs/sa_config.json')
        with open(config_path) as cfile:
            self.config = json.load(cfile)
        self.response_time = self.config.get('response_time', 2)

        self.num_goods = None
        self.goods = None
        self.valuations = {}
        self._goods_to_index = {}
        self._index_to_goods = {}

        self._is_national_bidder = False
        self.capacity = 3 
        self.vs_str = ""

        self.timeout = False
        self.global_timeout_count = 0
        self.round_number = 0

    def timeout_handler(self):
        print(f"{self.name} has timed out")
        self.timeout = True

    def handle_permissions(self, resp):
        self.player_type = resp.get('player_type')
        gh = self.game_report.game_history

        gh.setdefault('my_bid_history', []).append(resp.get('my_bid'))
        gh.setdefault('my_utils_history', []).append(resp.get('my_util'))
        gh.setdefault('my_payment_history', []).append(resp.get('payments'))
        gh.setdefault('price_history', []).append(resp.get('prices'))
        gh.setdefault('winner_history', []).append(resp.get('winners'))

    def handle_postround_data(self, resp):
        self.global_timeout_count = resp.get('global_timeout_count', 0)
        self.handle_permissions(resp)

    def is_national_bidder(self): 
        return self._is_national_bidder
    
    def get_bids(self):
        bid_dict = {}
        for good, val in self.valuations.items():
            if val > 0:
                bid_dict[good] = val
            else:
                bid_dict[good] = 0
        return bid_dict

    def get_action(self):
        return self.get_bids()

    def print_results(self):
        gh = self.game_report.game_history
        num_rounds = len(gh.get('my_utils_history', []))
        if num_rounds == 0:
            print(f"{self.name}: No rounds have been played yet.")
            return
        
        total_util = sum(gh.get('my_utils_history', []))
        avg_util = total_util / num_rounds

        bid_list = gh.get('my_bid_history', [])
        bid_avgs = []
        for bid in bid_list:
            if bid and isinstance(bid, dict) and len(bid) > 0:
                bid_avg = sum(bid.values()) / len(bid)
                bid_avgs.append(bid_avg)
        avg_bid = sum(bid_avgs) / len(bid_avgs) if bid_avgs else 0

        # Average payment per round (assumed to be a numeric value per round)
        payment_list = gh.get('my_payment_history', [])
        avg_payment = {}
        for payment in payment_list: 
            if payment and isinstance(payment, dict):
                for good, payment_val in payment.items():
                    if payment_val is not None:
                        avg_payment[good] = avg_payment.get(good, 0) + payment_val
        

        # Count winners across rounds.
        winners_list = gh.get('winner_history', [])
        winners_freq = {}
        for winners in winners_list:
            if winners and isinstance(winners, dict):
                for good, winner in winners.items():
                    if winner is not None:
                        winners_freq[winner] = winners_freq.get(winner, 0) + 1

        # Print summary
        print(self.vs_str)
        print(f"\n===== Overall Results for {self.name} =====")
        print(f"Rounds played: {num_rounds}")
        print(f"Total Utility: {total_util:.2f}")
        print(f"Average Utility per Round: {avg_util:.2f}")
        print(f"Average Bid Value per Round: {avg_bid:.2f}")
        print("Average Payments (across goods):")
        if avg_payment: 
            for good, payment in avg_payment.items():
                avg_payment[good] = payment / num_rounds
                print(f"  {good}: {avg_payment[good]:.2f}")
        else:
            print("  No payments recorded.")
        
        print("Average #Goods Won:")
        if winners_freq:
            for winner, freq in winners_freq.items():
                print(f"  {winner}: {freq / num_rounds} Goods Won")
        else:
            print("  No Allocations recorded.")
        print("============================================\n")

    def play(self):
        """
        Main loop for interacting with the GSVM-9 (or similar) server game.
        Listens for messages and responds appropriately.
        """
        # 1. Possibly read initial handshake
        data = self.client.recv(1024).decode()
        data = extract_first_json(data)
        if data:
            resp = json.loads(data)
            if resp.get('message') == 'provide_game_name':
                print(f"We are playing {resp.get('game_name')}")
                message = {"message": "game_name_recieved"}
                self.client.send(json.dumps(message).encode())
                self.restart()

        # 2. Main loop
        while True:
            data = self.client.recv(10000).decode()
            data = extract_first_json(data)
            if not data:
                continue
            request = json.loads(data)

            msg_type = request.get('message')
            if msg_type == 'send_preround_data':

                self._is_national_bidder = request.get('player_type', "regional") == "national"
                self.capacity = 6 if self._is_national_bidder else 3
                self.vs_str = request.get('vs_str', "")
                
                self.num_goods = request.get('num_goods')
                goods_list = request.get('goods', [])
                self.goods = set(goods_list)

                # Build index mappings
                self._goods_to_index = {good: idx for idx, good in enumerate(goods_list)}
                self._index_to_goods = {idx: good for good, idx in self._goods_to_index.items()}

                # Retrieve valuations from the server
                valuations_dict = request.get('valuations', {})
                self.valuations = {}
                for good in goods_list:
                    self.valuations[good] = valuations_dict.get(good, 0.0)

                # Acknowledge
                self.client.send(json.dumps({"message": "preround_data_recieved"}).encode())

            elif msg_type == 'request_bid':
                # The server wants our bid dictionary
                self.timeout = False
                try:
                    timer = threading.Timer(self.response_time, self.timeout_handler)
                    timer.start()
                    bid = self.get_action()
                finally:
                    if self.timeout:
                        bid = None
                    timer.cancel()

                try:
                    self.client.send(json.dumps({
                        "message": "provide_bid",
                        "bid": bid,
                        "timeout": self.timeout
                    }).encode())
                except Exception as e:
                    print(f"Error sending bid: {e}")

            elif msg_type == 'prepare_next_round':
                # The server is telling us the round is over
                self.handle_postround_data(request)
                self.update()
                self.client.send(json.dumps({"message": "ready_next_round"}).encode())

            elif msg_type == 'prepare_next_game':
                # The server is telling us the game ended and a new one will begin
                self.print_results()
                self.restart()
                self.client.send(json.dumps({"message": "ready_next_game"}).encode())

            elif msg_type == 'game_end':
                # The entire game is finished
                if request.get('send_results'):
                    try:
                        df = pd.read_json(request['results'])
                        if df is not None:
                            print(df)
                    except:
                        print("Results too large. Please check with your TA.")
                else:
                    print(request.get('results'))
                self.close()
                break

            elif msg_type == 'disqualified':
                # We were disqualified
                dq_msg = request.get('disqualification_message', '')
                if dq_msg:
                    print(dq_msg)
                self.close()
                break
