import logging
import json
import traceback
import asyncio
import random
import numpy as np
import pandas as pd
from itertools import product
from agt_server.server.games.game import Game
from itertools import combinations

class SuppressSocketSendError(logging.Filter):
    def filter(self, record):
        return "socket.send() raised exception" not in record.getMessage()

logger = logging.getLogger('asyncio')
logger.addFilter(SuppressSocketSendError())

class SAGame(Game):
    order_matters = False

    def __init__(self, server_config,
                 num_rounds=1000, player_data=[], player_types=[], permissions_map={},
                 game_kick_timeout=60, game_name="Simultaneous Auction", invalid_move_penalty=0,
                 timeout_tolerance=10):
        super().__init__(num_rounds, player_data, player_types, permissions_map,
                         game_kick_timeout, game_name, invalid_move_penalty, timeout_tolerance)
        self.server_config = server_config
        self.num_goods = self.server_config['num_goods']
        self.good_names = self.server_config.get('good_names', None)
        self.valuation_type = self.server_config.get('valuation_type', "additive")
        self.value_range = tuple(self.server_config.get('value_range', [0, 100]))
        self.price_history = []
        self.winner_history = []
        self.kth_price = self.server_config.get('kth_price', 1)
        self.game_name = f"{game_name} ({self.kth_price}th Price)"
        
        # Set up goods naming and mapping
        if self.good_names is not None:
            if len(self.good_names) !=self.num_goods:
                raise ValueError("Length of good_names must match num_goods")
            self._goods_to_index = {name: idx for idx, name in enumerate(self.good_names)}
            self.goods = set(self.good_names)
            self._index_to_goods = {idx: name for name, idx in self._goods_to_index.items()}
        else:
            self._goods_to_index = SAGame._name_goods(self.num_goods)
            self.goods = set(self._goods_to_index.keys())
            self._index_to_goods = {value: key for key, value in self._goods_to_index.items()}
        
        if self.valuation_type == 'additive':
            self.valuation_multiplier = 1
        elif self.valuation_type == 'complement':
            self.valuation_multiplier = 1.05
        elif self.valuation_type == 'substitute':
            self.valuation_multiplier = 0.95
        elif self.valuation_type == 'randomized':
            self.valuation_multiplier = 1.2
        
        over_bidding_parameter = 1.25
        base_value = self.value_range[1] * self.num_goods
        self.bid_upper_bound = base_value * self.valuation_multiplier ** (self.num_goods - 1) * over_bidding_parameter
        
        # Initialize game reports for each player (using address as the key)
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

    @staticmethod
    def _generate_sequence(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        yield from alphabet
        size = 2
        while True:
            for letters in product(alphabet, repeat=size):
                yield ''.join(letters)
            size += 1

    @staticmethod
    def _name_goods(size, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        alphabet_generator = SAGame._generate_sequence(alphabet)
        map_dict = {}
        for flat_index in range(size):
            letter = next(alphabet_generator)
            map_dict[letter] = flat_index
        return map_dict

    def compute_auction_result(self, bids):
        """
        For each good, determine the highest bid and assign the good accordingly.
        The winner pays the kth highest bid as determined by self.kth_price.
        
        Returns:
            allocation: dict mapping each good to the winning player's address.
            payments: dict mapping each player's address to their total payment.
        """
        allocation = {}
        # Initialize payments for each player by their address.
        payments = {data['name']: 0 for data in self.player_data}
        prices = {}

        for good in self.goods:
            bid_tuples = []
            # Collect all valid bids for the good.
            for addr, bid_bundle in bids.items():
                if bid_bundle is not None:
                    bid_value = bid_bundle.get(good, None)
                    if bid_value is not None and bid_value > 0:
                        bid_tuples.append((bid_value, addr))
            
            if bid_tuples:
                # Sort bids in descending order by bid value.
                sorted_bids = sorted(bid_tuples, key=lambda x: x[0], reverse=True)
                winner = sorted_bids[0][1]
                # Determine kth highest bid price.
                kth_index = self.kth_price - 1  # since list indices start at 0
                if kth_index < len(sorted_bids):
                    kth_bid = sorted_bids[kth_index][0]
                else:
                    # If there are fewer than kth bids, use the lowest bid available.
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


    async def run_game(self):
        """
        Runs the auction game asynchronously for a set number of rounds.
        """
        #print("Running auction game...")
        pairwise_adjustments = {}
        if self.valuation_type == 'randomized':
            for good1, good2 in combinations(self.goods, 2):
                pairwise_adjustments[(good1, good2)] = random.uniform(0.5, 1.5)
                    
        for round in range(self.num_rounds):
            print(f"Round {round + 1} of {self.num_rounds}")
            # --------------------
            # Preround: send valuations to each player.
            # --------------------
            for i, data in enumerate(self.player_data):
                player_type = self.player_types[i]
                writer, reader = data['client']
                # Generate random valuations for each good
                valuations = {good: random.randint(self.value_range[0], self.value_range[1]) for good in self.goods}
                self.game_reports[data['address']]["valuation_history"].append(valuations)
                pairwise_adjustments_serializable = {','.join(key): value for key, value in pairwise_adjustments.items()}
                message = {
                    "message": "send_preround_data",
                    "player_type": player_type,
                    "num_goods": self.num_goods,
                    "goods": list(self.goods),
                    "valuations": valuations,
                    "pairwise_adjustments": pairwise_adjustments_serializable,
                    "bid_upper_bound": self.bid_upper_bound
                }
                print(message)
                
                if not self.game_reports[data['address']]['disconnected']:
                    try:
                        writer.write(json.dumps(message).encode())
                        await writer.drain()
                        resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                        resp = json.loads(resp)
                        assert resp['message'] == 'preround_data_recieved', (
                            f"{data['name']} did not acknowledge preround data"
                        )
                    except asyncio.TimeoutError:
                        #print(f"{data['name']} Disqualified: Timed out on preround data")
                        self.game_reports[data['address']]['disqualification_message'] = (
                            f"{data['name']} Disqualified: Timed out on preround data"
                        )
                        self.game_reports[data['address']]['disconnected'] = True
                    except Exception as e:
                        stack_trace = traceback.format_exc()
                        #print(f"{data['name']} Disqualified on preround data: {type(e).__name__}: {e}\n{stack_trace}")
                        self.game_reports[data['address']]['disqualification_message'] = (
                            f"{data['name']} Disqualified on preround data: {type(e).__name__}: {e}\n{stack_trace}"
                        )
                        self.game_reports[data['address']]['disconnected'] = True
            
            # --------------------
            # Request bids from each player.
            # --------------------
            bids = {}
            for i, data in enumerate(self.player_data):
                writer, reader = data['client']
                if not self.game_reports[data['address']]['disconnected']:
                    message = {"message": "request_bid"}
                    try:
                        writer.write(json.dumps(message).encode())
                        await writer.drain()
                        resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                        resp = json.loads(resp)
                        if resp.get('timeout', False):
                            #print(f"{data['name']} Disqualified: Timed out on bid")
                            self.game_reports[data['address']]['bid_history'].append(None)
                            self.game_reports[data['address']]['timeout_count'] += 1
                            self.game_reports[data['address']]['global_timeout_count'] += 1
                            bids[data['name']] = None
                        else:
                            # Expecting a bid dictionary
                            bid = resp.get('bid', None)
                            self.game_reports[data['address']]['bid_history'].append(bid)
                            bids[data['name']] = bid
                            #print(f"Received bid from {data['name']}: {bid}")
                    except asyncio.TimeoutError:
                        self.game_reports[data['address']]['disqualification_message'] = (
                            f"{data['name']} Disqualified: Timed out on bid request"
                        )
                        #print(f"{data['name']} Disqualified: Timed out on bid request")
                        self.game_reports[data['address']]['disconnected'] = True
                        self.game_reports[data['address']]['bid_history'].append(None)
                        bids[data['name']] = None
                    except Exception as e:
                        stack_trace = traceback.format_exc()
                        self.game_reports[data['address']]['disqualification_message'] = (
                            f"{data['name']} Disqualified on bid request: {type(e).__name__}: {e}\n{stack_trace}"
                        )
                        #print(f"{data['name']} Disqualified on bid request: {type(e).__name__}: {e}\n{stack_trace}")
                        self.game_reports[data['address']]['disconnected'] = True
                        self.game_reports[data['address']]['bid_history'].append(None)
                        bids[data['name']] = None
                else:
                    #print("Warning: Player disconnected, skipping bid request.")
                    bids[data['name']] = None
            print(bids)
            # --------------------
            # Compute auction outcome
            # --------------------
            allocation, payments = self.compute_auction_result(bids)

            print(allocation, payments)
            # --------------------
            # Calculate round utilities for each player.
            # --------------------
            for data in self.player_data:
                valuations = self.game_reports[data['address']]['valuation_history'][-1]
                # Determine which goods the player won this round
                won_goods = [good for good, winner in allocation.items() if winner == data['name']]
                base_sum = sum(valuations.get(good, 0) for good in won_goods)
                total_payment = payments.get(data['name'], 0)
                n = len(won_goods)
                vt = self.valuation_type
                if vt == 'additive':
                    round_val = base_sum
                elif vt == 'complement':
                    round_val = base_sum * (1 + 0.05 * (n - 1)) if n > 0 else 0
                elif vt == 'substitute':
                    round_val = base_sum * (1 - 0.05 * (n - 1)) if n > 0 else 0
                elif vt == 'randomized':
                    new_valuations = valuations.copy()
                    for good1, good2 in combinations(won_goods, 2):
                        multiplier = pairwise_adjustments.get((good1, good2), 1.0)
                        new_valuations[good1] *= multiplier
                        new_valuations[good2] *= multiplier
                    
                    round_val = sum(new_valuations.get(good, 0) for good in won_goods)
                else:
                    round_val = base_sum
                round_util = round_val - total_payment
                # print(round_util)
                self.game_reports[data['address']]['util_history'].append(round_util)
            
            #print("Round Utilities:", {data['name']: self.game_reports[data['address']]['util_history'][-1] for data in self.player_data})
            
            # --------------------
            # Prepare for next round: send update message to players.
            # --------------------
            for i, data in enumerate(self.player_data):
                #print(i, len(self.player_data), len(self.player_types))
                player_type = self.player_types[i]
                #print(self.player_types[i])
                writer, reader = data['client']
                #print(writer, reader)
                opp_bid_history = [
                    bid for other in self.player_data 
                    if other['address'] != data['address']
                    for bid in [bids.get(other['name'])]
                    if bid is not None
                ]
                print(opp_bid_history)
                # print(data['address'])
                print(self.game_reports[data['address']])
                
                my_price = self.price_history[-1] if self.price_history else {}
                winner = self.winner_history[-1] if self.winner_history else {}
                my_bid = self.game_reports[data['address']]['bid_history'][-1] if self.game_reports[data['address']]['bid_history'] else {}
                my_util = self.game_reports[data['address']]['util_history'][-1] if self.game_reports[data['address']]['util_history'] else 0
                message = {
                    "message": "prepare_next_round",
                    "player_type": player_type,
                    "permissions": self.permissions_map.get(player_type, {}),
                    "my_bid": my_bid,
                    "my_util": my_util,
                    "payments": payments,
                    "prices": my_price,
                    "winners": winner,
                    "opp_bid_history": opp_bid_history,
                    "global_timeout_count": self.game_reports[data['address']]['global_timeout_count']
                }
                print(message)
                try:
                    # print(json.dumps(message))
                    # print(json.dumps(message).encode())
                    writer.write(json.dumps(message).encode())
                    await writer.drain()
                    resp = await asyncio.wait_for(reader.read(1024), timeout=self.kick_time)
                    if not resp:
                        # Handle the empty response case (e.g., mark the client as disconnected)
                        self.game_reports[data['address']]['disqualification_message'] = (
                            f"{data['name']} sent an empty response."
                        )
                        self.game_reports[data['address']]['disconnected'] = True
                        continue  # or break, depending on your logic
                    resp = json.loads(resp)

                    # print(resp)
                    # print("\n")
                    assert resp['message'] == 'ready_next_round', f"{data['name']} not ready for next round"
                except asyncio.TimeoutError:
                    self.game_reports[data['address']]['disqualification_message'] = (
                        f"{data['name']} Disqualified: Timed out on prepare_next_round"
                    )
                    #print(f"{data['name']} Disqualified: Timed out on prepare_next_round")
                    self.game_reports[data['address']]['disconnected'] = True
                except Exception as e:
                    stack_trace = traceback.format_exc()
                    # print(stack_trace)
                    self.game_reports[data['address']]['disqualification_message'] = (
                        f"{data['name']} error on prepare_next_round: {type(e).__name__}: {e}\n{stack_trace}"
                    )
                    #print(f"{data['name']} error on prepare_next_round: {type(e).__name__}: {e}\n{stack_trace}")
                    self.game_reports[data['address']]['disconnected'] = True
        #     print("Round complete.")
            

        # print("ENDING GAME?!?!?!")
        return self.game_reports

    def summarize_results(self):
        summary_data = []
        for data in self.player_data:
            addr = data['address']
            util_history = self.game_reports[addr].get('util_history', [])
            total_util = sum(util_history)
            avg_util = total_util / len(util_history) if util_history else 0
            summary_data.append([data['name'], total_util, avg_util])
        df = pd.DataFrame(summary_data, columns=["Player", "Total Utility", "Avg Utility Per Round"])
        df = df.sort_values(by="Total Utility", ascending=False)
        print(f"\nFinal Auction Results after {self.num_rounds} rounds:\n", df)
        return df

    def print_results(self, data):
        total_util = sum(self.game_reports[data['address']].get('util_history', []))
        print(f"{data['name']} got a total auction utility of {total_util}")
        return total_util
