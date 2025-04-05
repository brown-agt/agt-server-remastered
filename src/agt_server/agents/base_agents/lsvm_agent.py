from agt_server.agents.base_agents.agent import Agent
import json
import pandas as pd
import threading
import pkg_resources
import numpy as np
import random
from itertools import product

class MyLSVMAgent(Agent):
    def __init__(self, name=None, timestamp=None, config_path = 'configs/handin_configs/lsvm_config.json'):
        super().__init__(name, timestamp)
        
        config_path = pkg_resources.resource_filename('agt_server', config_path)
        with open(config_path) as cfile:
            server_config = json.load(cfile)
            
        self.response_time = server_config['response_time']
        self.shape = tuple(server_config['shape']) 
        self.num_goods = np.prod(self.shape)
        self._is_national_bidder = None
        self._valuations = None
        self._min_bids = np.zeros(self.shape)
        self._current_prices = np.zeros(self.shape)
        self._regional_good = None
        self._regional_size = int(server_config['regional_size'])
       
        self._goods_to_index = MyLSVMAgent._name_goods(self.shape)
        self._goods = set(self._goods_to_index.keys())
        self._index_to_goods = {value: key for key, value in self._goods_to_index.items()}
        self._current_round = 0 
        
        self.tentative_allocation = set()
    
    def get_regional_good(self): 
        """
        Return the regional good assigned to the agent.

        Returns:
        - regional_good: The specific good designated as the regional good for this agent.
        """
        return self._regional_good
    
    def get_goods(self): 
        """
        Get the set of goods names available in the auction.

        Returns:
        - A set of strings representing the names of the goods.
        """
        return self._goods 
    
    def is_national_bidder(self): 
        """
        Check if the agent is designated as a national bidder.

        Returns:
        - True if the agent is a national bidder, False otherwise.
        """
        return self._is_national_bidder
    
    def get_shape(self): 
        """
        Get the shape of the goods space as a tuple.

        Returns:
        - A tuple representing the dimensions of the goods space.
        """
        return self.shape 
    
    def get_num_goods(self): 
        """
        Get the total number of goods available.

        Returns:
        - An integer representing the total number of goods.
        """
        return self.num_goods
        
    def get_goods_to_index(self): 
        """
        Get the mapping from goods names to their index in the goods space.

        Returns:
        - A dictionary mapping string names to tuple indices.
        """
        return self._goods_to_index
    
    def get_tentative_allocation(self): 
        """
        Get the current tentative allocation of goods to this agent.

        Returns:
        - A set of goods (strings) currently tentatively allocated to this agent.
        """
        return self.tentative_allocation

    def get_partitions(self, bundle = None): 
        """
        Calculate the partitions of a bundle for the regional or national bidder.
        
        :param bundle: A set of strings, where each strings represents the name of a good
        :return: A list of connected partitions of the bundle of goods
        """
        def _is_adjacent(item1, item2):
            i1_idx = self._goods_to_index[item1]
            i2_idx = self._goods_to_index[item2]
            return sum([abs(i1_idx[i] - i2_idx[i]) for i in range(len(i1_idx))]) == 1

        def _dfs(current, visited, component, all_goods):
            visited.add(current)
            component.add(current)
            for neighbor in all_goods:
                if neighbor not in visited and _is_adjacent(current, neighbor):
                    _dfs(neighbor, visited, component, all_goods)

        def _get_partitions(all_goods):
            visited = set()
            partitions = []
            for good in all_goods:
                if good not in visited:
                    component = set()
                    _dfs(good, visited, component, all_goods)
                    partitions.append(component)
            return partitions
    
        partitions = _get_partitions(list(bundle))
        return partitions
    
    def calc_total_valuation(self, bundle = None):
        """
        Calculate the valuation of a bundle for the regional or national bidder.
        
        :param bundle: A set of strings, where each strings represents the name of a good
        :return: The valuation of the bundle.
        """
        if bundle is None: 
            bundle = self.tentative_allocation
            
        if self._is_national_bidder:
            a = 320
            b = 10
        else:
            a = 160
            b = 4
        
        base_values = {good: self._valuations[self._goods_to_index[good]] for good in bundle}
        partitions = self.get_partitions(bundle)
        
        valuation = 0
        for C in partitions:
            partition_valuation = sum(base_values[idx] for idx in C)
            valuation += (1 + a / (100 * (1 + np.exp(b - len(C))))) * partition_valuation
        return valuation
    
    def calc_total_prices(self, bundle = None):
        """
        Calculate the prices of a bundle for the regional or national bidder.
        
        :param bundle: A set of strings, where each strings represents the name of a good
        :return: The prices of the bundle.
        """
        if bundle is None: 
            bundle = self.tentative_allocation
            
        return sum([self._current_prices[self._goods_to_index[good]] for good in bundle])
         
        
    def calc_total_utility(self, bundle = None):
        """
        Calculate the utility of a bundle for the regional or national bidder.
        
        :param bundle: A set of strings, where each strings represents the name of a good
        :return: The utility of the bundle.
        """
        valuation = self.calc_total_valuation(bundle)
        prices = self.calc_total_prices(bundle) 
        return valuation - prices        

    def calculate_tentative_valuation(self): 
        """
        Calculates the total bundle valuation of the tentative allocation.
        
        Returns:
        - float: The calculated utility value.
        """
        return self.calc_bundle_valuation(self.tentative_allocation)
        
    def get_current_round(self): 
        """
        Retrieves the current round number.
        
        Returns:
        - int: The current round number.
        """
        return self._current_round
        
    def get_goods_in_proximity(self): 
        """
        Retrieves the names of goods that are within the agent's proximity.
        Includes all goods if the agent is a National Bidder.
        
        Returns:
        - list: A list of goods' names within the agent's proximity.
        """
        if self._is_national_bidder:
            return list(self._index_to_goods.values())
        else:
            non_zero_indices = np.argwhere(self._valuations != 0)
            non_zero_indices_tuples = [tuple(idx) for idx in non_zero_indices]
            return [self._index_to_goods[idx] for idx in non_zero_indices_tuples if idx in self._index_to_goods]
        
    
    def proximity(self, arr = None, regional_good = None):
        """
        Filters the valuation array to only include valuations within a specified distance from a regional good.
        
        Parameters:
        - arr (numpy.ndarray, optional): The valuation array to filter. If None, uses the agent's valuations.
        - regional_good (str, optional): The regional good used as the center for filtering. If None, uses the agent's regional good.
        
        Returns:
        - numpy.ndarray: A masked array with valuations outside the specified distance set to 0.
        """
        if arr is None: 
            arr = self._valuations
        if regional_good is None: 
            regional_good = self._regional_good
        
        index = self._goods_to_index[regional_good]
        grid = np.ogrid[tuple(slice(0, max_shape) for max_shape in arr.shape)]
        distance = sum(np.abs(g - idx) for g, idx in zip(grid, index))
        masked_arr = np.where(distance <= self._regional_size, arr, 0)
        return masked_arr
    
    @staticmethod
    def _generate_sequence(alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        """
        Generates an infinite sequence of strings based on the provided alphabet.
        
        Parameters:
        - alphabet (str, optional): The alphabet to use for generating the sequence. Defaults to 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.
        
        Yields:
        - str: The next string in the sequence.
        """
        yield from alphabet 
        size = 2 
        while True:
            for letters in product(alphabet, repeat=size):
                yield ''.join(letters)
            size += 1
        
    @staticmethod
    def _name_goods(shape, alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        """
        Names the goods in a multidimensional world of a given shape using an alphabet.
        
        Parameters:
        - shape (tuple): The shape of the world.
        - alphabet (str, optional): The alphabet used for naming goods.
        
        Returns:
        - dict: A mapping from string names to multidimensional indices.
        """
        alphabet_generator = MyLSVMAgent._generate_sequence(alphabet)
        map_dict = {}
        total_elements = np.prod(shape)
        
        for flat_index in range(total_elements):
            multidimensional_index = np.unravel_index(flat_index, shape)
            letter = next(alphabet_generator)
            map_dict[letter] = multidimensional_index
                        
        return map_dict

    def get_valuation_as_array(self): 
        """
        Retrieves the agent's valuation as a numpy array.
        
        Returns:
        - numpy.ndarray: The valuation array.
        """
        return self._valuations
    
    def get_valuation(self, good): 
        """
        Retrieves the valuation for a specific good.
        
        Parameters:
        - good (str): The name of the good.
        
        Returns:
        - float: The valuation for the specified good.
        """
        return self._valuations[self._goods_to_index[good]]
    
    def get_valuations(self, bundle = None): 
        """
        Retrieves the valuations for a set of goods.
        
        Parameters:
        - bundle (set, optional): A set of goods for which valuations are retrieved. If None, uses all goods.
        
        Returns:
        - dict: A mapping from goods to their valuations.
        """
        if bundle is None: 
            bundle = self._goods
        return {good: self._valuations[self._goods_to_index[good]] for good in bundle}
    
    def get_min_bids_as_array(self): 
        """
        Retrieves the minimum bids as a numpy array.
        
        Returns:
        - numpy.ndarray: The array of minimum bids.
        """
        return self._min_bids 
    
    def get_min_bids(self, bundle = None): 
        """
        Retrieves the minimum bids for a set of goods.
        
        Parameters:
        - bundle (set, optional): A set of goods for which minimum bids are retrieved. If None, uses all goods.
        
        Returns:
        - dict: A mapping from goods to their minimum bids.
        """
        if bundle is None: 
            bundle = self._goods
        return {good: self._min_bids[self._goods_to_index[good]] for good in bundle if good in self._goods_to_index}

    def is_valid_bid_bundle(self, my_bids):
        """
        Checks whether a bundle of bids is valid according to the agent's constraints and the game's rules.
        
        Parameters:
        - my_bids (dict): A dictionary mapping goods to bid values.
        
        Returns:
        - bool: True if the bid bundle is valid, False otherwise.
        """
        
        if not isinstance(my_bids, dict):
            print("NOT VALID: my_bids must be of type Dict[str, float]")
            return False
        
        for good, bid in my_bids.items():
            if bid is None:
                print(f"NOT VALID: bid for good {good} cannot be None")
                return False

            if good not in self._goods_to_index or bid < self._min_bids[self._goods_to_index[good]]:
                print(f"NOT VALID: bid for good {good} cannot be less than the min bid")
                return False

            price_history = self.game_report.game_history['price_history']
            bid_history = self.game_report.game_history['my_bid_history']
            for past_prices, past_bids in zip(price_history, bid_history):
                price_diff = self._current_prices - past_prices
                bid_diff = my_bids - past_bids
                switch_cost = np.dot(price_diff, bid_diff)
                if switch_cost > 0:
                    print(f"NOT VALID: New bids are {switch_cost} relatively more expensive than maintaining the old bids, strategy is insincere")
                    return False  
        return True 
        
    def clip_bids(self, my_bids):
        """
        Ensures that all bids in a bid bundle are at least as high as the minimum bids for the corresponding goods.

        Parameters:
        - my_bids (dict): A dictionary mapping goods to bid values.

        Returns:
        - dict: A dictionary with the bid values adjusted to be no lower than the minimum bid requirements.
        """
        for good in my_bids: 
            my_bids[good] = max(my_bids[good], self._min_bids[self._goods_to_index[good]])
        return my_bids

    def clip_bid(self, good, bid): 
        """
        Clips a single bid for a good to ensure it meets or exceeds the minimum bid.

        Parameters:
        - good (str): The good for which the bid is being placed.
        - bid (float): The bid value for the good.

        Returns:
        - float: The adjusted bid value, which will be no lower than the minimum required bid for the specified good.
        """
        return max(bid, self._min_bids[self._goods_to_index[good]])
    
    def timeout_handler(self):
        """
        Handles timeout situations by setting the agent's timeout status and potentially performing other necessary actions.
        """
        print(f"{self.name} has timed out")
        self.timeout = True

    def handle_postround_data(self, resp):
        """
        Processes post-round data received from the server, updating the agent's state accordingly.

        Parameters:
        - resp (dict): A dictionary containing post-round data from the server.
        """
        self.global_timeout_count = resp['global_timeout_count']
        self.curr_opps = resp['opp_names']
        self.handle_permissions(resp)

    def map_to_ndarray(self, map, object = False): 
        """
        Converts a mapping of goods to values into a numpy array with the agent's valuation shape.

        Parameters:
        - map (dict): A dictionary mapping goods to values.
        - object (bool, optional): Whether to create an array of objects. Defaults to False.

        Returns:
        - numpy.ndarray: An array representing the mapping, in the shape of the agent's valuation.
        """
        if object: 
            arr = np.empty(self.shape, dtype=object)
        else: 
            arr = np.zeros(self.shape)
        for item in map: 
            arr[self._goods_to_index[item]] = map[item]
        return arr

    def ndarray_to_map(self, arr): 
        """
        Converts a numpy array into a dictionary mapping goods to values, based on the agent's goods' indexing.

        Parameters:
        - arr (numpy.ndarray): The array to convert.

        Returns:
        - dict: A dictionary mapping goods to their values in the array.
        """
        return {good: arr[self._goods_to_index[good]] for good in self.get_goods()}
                        
    def get_game_report(self): 
        """
        Retrieves the game report containing the history and outcomes of all the rounds the agent has participated in.

        Returns:
        - GameReport: The game report object.
        """
        return self.game_report

    def get_util_history(self):
        """
        Retrieves the utility history for the agent, showing how the agent's utility has changed over time.

        Returns:
        - list: A list of utility values, one for each round.
        """
        return self.game_report.get_util_history()

    def get_bid_history(self): 
        """
        Retrieves the history of bids made during the game [AS A NDARRAY].

        :return: A list of bids (np.ndarrays) if available; otherwise, an empty list.
        """
        return self.game_report.get_bid_history()
    
    def get_bid_history_map(self): 
        """
        Retrieves the history of bids made during the game [AS A MAP].

        :return: A list of bid (maps from goods to value) if available; otherwise, an empty list.
        """
        return self.game_report.get_bid_history_map()
    
    def get_price_history(self): 
        """
        Retrieves the history of prices during the game [AS A NDARRAY].

        :return: A list of prices (np.ndarrays) if available; otherwise, an empty list.
        """
        return self.game_report.get_price_history()
    
    def get_price_history_map(self): 
        """
        Retrieves the history of prices during the game [AS A MAP].

        :return: A list of prices (maps from goods to value) if available; otherwise, an empty list.
        """
        return self.game_report.get_price_history_map()
    
    def get_winner_history(self): 
        """
        Retrieves the history of tentative winners during the game [AS A NDARRAY of OBJECTS].

        :return: A list of winners (np.ndarrays) if available; otherwise, an empty list.
        """
        return self.game_report.get_winner_history()
    
    def get_winner_history_map(self): 
        """
        Retrieves the history of tentative winners during the game [AS A MAP].

        :return: A list of winners (maps from goods to winner) if available; otherwise, an empty list.
        """
        return self.game_report.get_winner_history_map() 
    
    def get_previous_util(self):
        """
        Retrieves the most recent utility value for the agent.

        Returns:
        - float: The last utility value recorded for the agent.
        """
        return self.game_report.get_previous_util()
    
    def get_previous_bid(self):
        """
        Retrieves the most recent entry from the bid history as a ndarray. 
        :return: The latest bids if available; otherwise, None.
        """
        return self.game_report.get_previous_bid()

    def get_previous_bid_map(self):
        """
        Retrieves the most recent entry from the bid history as a map. 
        :return: The latest bids if available; otherwise, None.
        """
        return self.game_report.get_previous_bid_map()
    
    def get_current_prices(self): 
        """
        Retrieves the most recent entry from the price history as a ndarray. 
        :return: The latest price if available; otherwise, None.
        """
        return self.game_report.get_previous_price()
    
    def get_current_prices_map(self): 
        """
        Retrieves the most recent entry from the price history as a map. 
        :return: The latest price if available; otherwise, None.
        """
        return self.game_report.get_previous_price_map()
    
    def get_previous_winners(self): 
        """
        Retrieves the most recent entry from the tentative winners history as a ndarray. 
        :return: The latest winners if available; otherwise, None.
        """
        return self.game_report.get_previous_winners()
    
    def get_previous_winners_map(self): 
        """
        Retrieves the most recent entry from the tentative winners history as a map. 
        :return: The latest winners if available; otherwise, None.
        """
        return self.game_report.get_previous_winners_map()
    