import logging
import json
import traceback
import asyncio
import random
import numpy as np
import pandas as pd
from itertools import product
from agt_server.server.games.game import Game

class SuppressSocketSendError(logging.Filter):
    def filter(self, record):
        return "socket.send() raised exception" not in record.getMessage()

logger = logging.getLogger('asyncio')
logger.addFilter(SuppressSocketSendError())

class GSVM9Game(Game):
    def __init__(self, server_config, num_rounds=10, player_data=[], player_types=[], permissions_map={},
                 game_kick_timeout=60, game_name="GSVM-9 Auction", invalid_move_penalty=0,
                 timeout_tolerance=10):
        super().__init__(num_rounds - 1, player_data, player_types, permissions_map,
                         game_kick_timeout, game_name, invalid_move_penalty, timeout_tolerance)

        self.server_config = server_config
        self.num_goods = server_config.get("num_goods", 9)
        self.goods = server_config.get("goods", None)
        
        self.valuation_type = "complement"
        self.game_name = "GSVM-9 Auction"
        self.kth_price = server_config.get("kth_price", 1)

        self.max_valuations_national = server_config.get("max_valuations_national", None)
        self.max_valuations_regional = [
            {"A":20, "B":20, "C":40, "D":40, "E":20, "F":0,  "G":20, "H":0,  "I":0},
            {"A":0,  "B":40, "C":40, "D":20, "E":20, "F":0,  "G":0,  "H":20, "I":0},
            {"A":20, "B":20, "C":0,  "D":20, "E":20, "F":20, "G":0,  "H":0,  "I":20}
        ]
        
        self._goods_to_index = {name: idx for idx, name in enumerate(self.goods)}
        self._index_to_goods = {idx: name for name, idx in self._goods_to_index.items()}
        
        for data in self.player_data:
            self.game_reports[data['address']] = {
                "valuation_history": [],
                "bid_history": [],
                "util_history": [],
                "timeout_count": 0,
                "global_timeout_count": 0,
                "disconnected": False,
                "disqualification_message": ""
            }
        self.price_history = []
        self.winner_history = []

    async def run_game(self):
        for round in range(self.num_rounds):
            #print(f"Round: {round}")
            # --- Preround: Send valuations ---
            for i, data in enumerate(self.player_data):
                writer, reader = data['client']
                player_type = self.player_types[i]
                #print(player_type)
                # Generate valuations based on role:
                if player_type.lower() == "national":
                    valuations = {good: random.uniform(0, self.max_valuations_national[good]) for good in self.goods}
                else:
                    # Assume player_type is like "regional1", "regional2", etc.
                    try:
                        idx = int(''.join(filter(str.isdigit, player_type))) - 1
                    except:
                        idx = i - 1  # Fallback
                    valuations = {good: random.uniform(0, self.max_valuations_regional[idx][good]) for good in self.goods}
                
                self.game_reports[data['address']]["valuation_history"].append(valuations)
                message = {
                    "message": "send_preround_data",
                    "player_type": player_type,
                    "vs_str":  " VS ".join([f"{d['name']} ({self.player_types[j]})" for j, d in enumerate(self.player_data)]),
                    "num_goods": self.num_goods,
                    "goods": self.goods,
                    "valuations": valuations
                }
               
                print(" VS ".join([f"{d['name']} ({self.player_types[j]})" for j, d in enumerate(self.player_data)]))
                # print("Sending preround data to", data['name'])
                # print(message)
                if not self.game_reports[data['address']]['disconnected']:
                    try:
                        writer.write(json.dumps(message).encode())
                        await writer.drain()
                        resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                        resp = json.loads(resp)
                        assert resp['message'] == 'preround_data_recieved', f"{data['name']} did not acknowledge preround data"
                    except asyncio.TimeoutError:
                        self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} Disqualified: Timed out on preround data"
                        self.game_reports[data['address']]['disconnected'] = True
                    except Exception as e:
                        stack_trace = traceback.format_exc()
                        self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} Disqualified on preround data: {type(e).__name__}: {e}\n{stack_trace}"
                        self.game_reports[data['address']]['disconnected'] = True

            # --- Request Bids ---
            bids = {}
            for i, data in enumerate(self.player_data):
                writer, reader = data['client']
                if not self.game_reports[data['address']]['disconnected']:
                    message = {"message": "request_bid"}
                    #print("Sending bid request to", data['name'])
                    try:
                        writer.write(json.dumps(message).encode())
                        await writer.drain()
                        resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                        resp = json.loads(resp)
                        if resp.get('timeout', False):
                            print(f"{data['name']} timed out on bid request")
                            self.game_reports[data['address']]['bid_history'].append(None)
                            self.game_reports[data['address']]['timeout_count'] += 1
                            self.game_reports[data['address']]['global_timeout_count'] += 1
                            bids[data['name']] = None
                        else:
                            bid = resp.get('bid', None)
                            #print(bid)
                            self.game_reports[data['address']]['bid_history'].append(bid)
                            bids[data['name']] = bid
                    except asyncio.TimeoutError:
                        self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} Disqualified: Timed out on bid request"
                        self.game_reports[data['address']]['disconnected'] = True
                        self.game_reports[data['address']]['bid_history'].append(None)
                        bids[data['name']] = None
                    except Exception as e:
                        stack_trace = traceback.format_exc()
                        self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} Disqualified on bid request: {type(e).__name__}: {e}\n{stack_trace}"
                        self.game_reports[data['address']]['disconnected'] = True
                        self.game_reports[data['address']]['bid_history'].append(None)
                        bids[data['name']] = None
                else:
                    bids[data['name']] = None

            # --- Compute Auction Outcome ---
            #print(f"Computing auction outcome with {bids}")
            allocation, payments = self.compute_auction_result(bids)
            # print(allocation, payments)

            # --- Compute Synergy-Based Utilities ---
            for data in self.player_data:
                valuations = self.game_reports[data['address']]['valuation_history'][-1]
                # Determine which goods this player won.
                won_goods = [good for good, winner in allocation.items() if winner == data['name']]
                base_sum = sum(valuations.get(g, 0) for g in won_goods)
                n = len(won_goods)
                synergy_val = (1 + 0.2*(n-1)) * base_sum if n > 0 else 0
                total_payment = payments.get(data['name'], 0)
                round_util = synergy_val - total_payment
                self.game_reports[data['address']]['util_history'].append(round_util)

            # --- Prepare for Next Round ---
            for i, data in enumerate(self.player_data):
                player_type = self.player_types[i]
                writer, reader = data['client']
                message = {
                    "message": "prepare_next_round",
                    "player_type": player_type,
                    "permissions": self.permissions_map.get(player_type, {}),
                    "my_bid": self.game_reports[data['address']]['bid_history'][-1],
                    "my_util": self.game_reports[data['address']]['util_history'][-1],
                    "payments": payments,
                    "prices": self.price_history[-1] if self.price_history else {},
                    "winners": self.winner_history[-1] if self.winner_history else {},
                    "global_timeout_count": self.game_reports[data['address']]['global_timeout_count']
                }
                # print("Sending prepare next round to", data['name'])
                # print(message)
                try:
                    writer.write(json.dumps(message).encode())
                    await writer.drain()
                    resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                    resp = json.loads(resp)
                    assert resp['message'] == 'ready_next_round', f"{data['name']} not ready for next round"
                except asyncio.TimeoutError:
                    self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} Disqualified: Timed out on prepare_next_round"
                    self.game_reports[data['address']]['disconnected'] = True
                except Exception as e:
                    stack_trace = traceback.format_exc()
                    self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} error on prepare_next_round: {type(e).__name__}: {e}\n{stack_trace}"
                    self.game_reports[data['address']]['disconnected'] = True

        # --- Prepare for Next Game -- 
        for i, data in enumerate(self.player_data):
            writer, reader = data['client']
            message = {"message": "prepare_next_game"}
            # print("Sending game over to", data['name'])
            # print(message)
            if not self.game_reports[data['address']]['disconnected']:
                try:
                    writer.write(json.dumps(message).encode())
                    await writer.drain()
                    resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                    resp = json.loads(resp)
                    assert resp['message'] == 'ready_next_game', f"{data['name']} did not acknowledge game over"
                except asyncio.TimeoutError:
                    self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} Disqualified: Timed out on game_over"
                    self.game_reports[data['address']]['disconnected'] = True
                except Exception as e:
                    stack_trace = traceback.format_exc()
                    self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} Disqualified on game_over: {type(e).__name__}: {e}\n{stack_trace}"
                    self.game_reports[data['address']]['disconnected'] = True

        return self.game_reports

    def compute_auction_result(self, bids):
        """
        For each good, determine the highest bid among all players.
        The winner pays the kth highest bid (kth_price).
        Returns:
          allocation: dict mapping each good to the winning player's name.
          payments: dict mapping each player's name to their total payment.
        """
        allocation = {}
        payments = {data['name']: 0 for data in self.player_data}
        prices = {}
        for good in self.goods:
            bid_tuples = []
            for addr, bid_bundle in bids.items():
                if bid_bundle is not None:
                    bid_value = bid_bundle.get(good, None)
                    if bid_value is not None and bid_value > 0:
                        bid_tuples.append((bid_value, addr))
            if bid_tuples:
                sorted_bids = sorted(bid_tuples, key=lambda x: x[0], reverse=True)
                winner = sorted_bids[0][1]
                kth_index = self.kth_price - 1
                if kth_index < len(sorted_bids):
                    kth_bid = sorted_bids[kth_index][0]
                else:
                    kth_bid = sorted_bids[-1][0]
            else:
                winner = None
                kth_bid = None
            allocation[good] = winner
            prices[good] = kth_bid
            if winner is not None and kth_bid is not None:
                payments[winner] += kth_bid
        self.price_history.append(prices)
        self.winner_history.append(allocation)
        return allocation, payments

    async def run_game_final(self):
        """
        Notifies players that the game is over and they should prepare for the next game.
        """
        message = {"message": "prepare_next_game"}
        for data in self.player_data:
            if not self.game_reports[data['address']]['disconnected']:
                try:
                    writer, reader = data['client']
                    writer.write(json.dumps(message).encode())
                    await writer.drain()
                    resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                    resp = json.loads(resp)
                    assert resp['message'] == 'ready_next_game', f"{data['name']} not ready for next game"
                except asyncio.TimeoutError:
                    self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} Disqualified: Timed out on prepare_next_game"
                    self.game_reports[data['address']]['disconnected'] = True
                except Exception as e:
                    stack_trace = traceback.format_exc()
                    self.game_reports[data['address']]['disqualification_message'] = f"{data['name']} error on prepare_next_game: {type(e).__name__}: {e}\n{stack_trace}"
                    self.game_reports[data['address']]['disconnected'] = True
        return self.game_reports

    def summarize_results(self):
        """
        Summarizes the game results across all rounds.
        """
        summary_data = []
        for data in self.player_data:
            addr = data['address']
            util_history = self.game_reports[addr].get('util_history', [])
            total_util = sum(util_history)
            avg_util = total_util / len(util_history) if util_history else 0
            summary_data.append([data['name'], total_util, avg_util])
        df = pd.DataFrame(summary_data, columns=["Player", "Total Utility", "Avg Utility Per Round"])
        df = df.sort_values(by="Total Utility", ascending=False)
        print(f"\nFinal GSVM-9 Auction Results after {self.num_rounds} rounds:\n", df)
        return df
