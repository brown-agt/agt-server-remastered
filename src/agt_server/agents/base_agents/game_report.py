from collections import defaultdict
class GameReport(): 
    def __init__(self) -> None:
        self.game_history = defaultdict(lambda: [])
        
    def __str__(self) -> str:
        return f"Game Report: \n {self.game_history}"
    
    def __repr__(self) -> str:
        return self.__str__()

    def get_game_report_as_dict(self): 
        """
        Retrieves the entire game history as a dictionary.

        :return: The game_history attribute containing all recorded game data.
        """
        return self.game_history
    
    def get_action_history(self):
        """
        Retrieves the history of actions performed by the current player.

        :return: A list of the current player's actions if available; otherwise, an empty list.
        """
        if 'my_action_history' in self.game_history:
            return self.game_history['my_action_history']
        else: 
            return []

    def get_util_history(self):
        """
        Retrieves the utility history for the current player.

        :return: A list of utility values for the current player if available; otherwise, an empty list.
        """
        if 'my_utils_history' in self.game_history:
            return self.game_history['my_utils_history']
        else: 
            return []


    def get_opp_action_history(self):
        """
        Retrieves the action history for the opponent player.

        :return: A list of the opponent player's actions if available; otherwise, an empty list.
        """
        if 'opp_action_history' in self.game_history:
            return self.game_history['opp_action_history']
        else: 
            return []

    def get_opp1_action_history(self): 
        """
        Retrieves the action history for the first opponent player in games with multiple opponents.

        :return: A list of the first opponent player's actions if available; otherwise, an empty list.
        """
        if "opp1_action_history" in self.game_history:
            return self.game_history['opp1_action_history']
        else: 
            return []

    
    def get_opp2_action_history(self): 
        """
        Retrieves the action history for the second opponent player in games with multiple opponents.

        :return: A list of the second opponent player's actions if available; otherwise, an empty list.
        """
        if "opp2_action_history" in self.game_history:
            return self.game_history['opp2_action_history']
        else: 
            return []

    def get_opp_util_history(self):
        """
        Retrieves the utility history for the opponent player.

        :return: A list of utility values for the opponent player if available; otherwise, an empty list.
        """
        if 'opp_utils_history' in self.game_history:
            return self.game_history['opp_utils_history']
        else: 
            return []
    
    def get_opp1_util_history(self):
        """
        Retrieves the utility history for the first opponent player in games with multiple opponents.

        :return: A list of utility values for the first opponent player if available; otherwise, an empty list.
        """ 
        if "opp1_utils_history" in self.game_history:
            return self.game_history['opp1_utils_history']
        else: 
            return []
    
    def get_opp2_util_history(self): 
        """
        Retrieves the utility history for the second opponent player in games with multiple opponents.

        :return: A list of utility values for the second opponent player if available; otherwise, an empty list.
        """
        if "opp2_utils_history" in self.game_history:
            return self.game_history['opp2_utils_history']
        else: 
            return []
    
    def get_mood_history(self):
        """
        Retrieves the mood history for the game, reflecting the emotional state or mood changes over time.

        :return: A list of mood states throughout the game if available; otherwise, an empty list.
        """
        if 'mood_history' in self.game_history:
            return self.game_history['mood_history']
        else: 
            return []
    
    def get_bid_history(self): 
        """
        Retrieves the history of bids made during the game [AS A NDARRAY].

        :return: A list of bids (np.ndarrays) if available; otherwise, an empty list.
        """
        if 'bid_history' in self.game_history:
            return self.game_history['bid_history']
        else: 
            return []
    
    def get_bid_history_map(self): 
        """
        Retrieves the history of bids made during the game [AS A MAP].

        :return: A list of bid (maps from goods to value) if available; otherwise, an empty list.
        """
        if 'bid_history_map' in self.game_history:
            return self.game_history['bid_history_map']
        else: 
            return []
        
    def get_price_history(self): 
        """
        Retrieves the history of prices during the game [AS A NDARRAY].

        :return: A list of prices (np.ndarrays) if available; otherwise, an empty list.
        """
        if 'price_history' in self.game_history:
            return self.game_history['price_history']
        else: 
            return []
    
    def get_price_history_map(self): 
        """
        Retrieves the history of prices during the game [AS A MAP].

        :return: A list of prices (maps from goods to value) if available; otherwise, an empty list.
        """
        if 'price_history_map' in self.game_history:
            return self.game_history['price_history_map']
        else: 
            return []
    
    def get_winner_history(self): 
        """
        Retrieves the history of tentative winners during the game [AS A NDARRAY of OBJECTS].

        :return: A list of winners (np.ndarrays) if available; otherwise, an empty list.
        """
        if 'winner_history' in self.game_history:
            return self.game_history['winner_history']
        else: 
            return []
    
    def get_winner_history_map(self): 
        """
        Retrieves the history of tentative winners during the game [AS A MAP].

        :return: A list of winners (maps from goods to winner) if available; otherwise, an empty list.
        """
        if 'winner_history_map' in self.game_history:
            return self.game_history['winner_history_map']
        else: 
            return []

    def get_last_action(self):
        """
        Retrieves the last action performed by the current player.

        :return: The most recent action of the current player if available; otherwise, None.
        """
        if 'my_action_history' in self.game_history and len(self.game_history['my_action_history']) > 0:
            return self.game_history['my_action_history'][-1]
        
    def get_previous_util(self):
        """
        Retrieves the last utility value for the current player.

        :return: The most recent utility value of the current player if available; otherwise, None.
        """
        if 'my_utils_history' in self.game_history and len(self.game_history['my_utils_history']) > 0:
            return self.game_history['my_utils_history'][-1]

    def get_opp_last_action(self):
        """
        Retrieves the last action performed by the opponent player.

        :return: The most recent action of the opponent player if available; otherwise, None.
        """
        if 'opp_action_history' in self.game_history and len(self.game_history['opp_action_history']) > 0:
            return self.game_history['opp_action_history'][-1]

    def get_opp1_last_action(self):
        """
        Retrieves the last action performed by the first opponent player in games with multiple opponents.

        :return: The most recent action of the first opponent player if available; otherwise, None.
        """
        if 'opp1_action_history' in self.game_history and len(self.game_history['opp1_action_history']) > 0:
            return self.game_history['opp1_action_history'][-1]
    
    def get_opp2_last_action(self):
        """
        Retrieves the last action performed by the second opponent player in games with multiple opponents.

        :return: The most recent action of the second opponent player if available; otherwise, None.
        """
        if 'opp2_action_history' in self.game_history and len(self.game_history['opp2_action_history']) > 0:
            return self.game_history['opp2_action_history'][-1]
    
    def get_opp_last_util(self):
        """
        Retrieves the last utility value for the opponent player.

        :return: The most recent utility value of the opponent player if available; otherwise, None.
        """
        if 'opp_utils_history' in self.game_history and len(self.game_history['opp_utils_history']) > 0:
            return self.game_history['opp_utils_history'][-1]
    
    def get_opp1_last_util(self):
        """
        Retrieves the last utility value for the first opponent player in games with multiple opponents.

        :return: The most recent utility value of the first opponent player if available; otherwise, None.
        """
        if 'opp1_utils_history' in self.game_history and len(self.game_history['opp1_utils_history']) > 0:
            return self.game_history['opp1_utils_history'][-1]
    
    def get_opp2_last_util(self):
        """
        Retrieves the last utility value for the second opponent player in games with multiple opponents.

        :return: The most recent utility value of the second opponent player if available; otherwise, None.
        """
        if 'opp2_utils_history' in self.game_history and len(self.game_history['opp2_utils_history']) > 0:
            return self.game_history['opp2_utils_history'][-1]
    
    def get_last_mood(self):
        """
        Retrieves the most recent mood state from the mood history.

        :return: The latest mood state if available; otherwise, None.
        """
        if 'mood_history' in self.game_history and len(self.game_history['mood_history']) > 0:
            return self.game_history['mood_history'][-1]

    def get_previous_bid(self):
        """
        Retrieves the most recent entry from the bid history as a ndarray. 
        :return: The latest bids if available; otherwise, None.
        """
        if 'bid_history' in self.game_history and len(self.game_history['bid_history']) > 0:
            return self.game_history['bid_history'][-1]
    
    def get_previous_bid_map(self):
        """
        Retrieves the most recent entry from the bid history as a map. 
        :return: The latest bids if available; otherwise, None.
        """
        if 'bid_history_map' in self.game_history and len(self.game_history['bid_history_map']) > 0:
            return self.game_history['bid_history_map'][-1]
    
    def get_previous_price(self): 
        """
        Retrieves the most recent entry from the price history as a ndarray. 
        :return: The latest price if available; otherwise, None.
        """
        if 'price_history' in self.game_history and len(self.game_history['price_history']) > 0:
            return self.game_history['price_history'][-1]
    
    def get_previous_price_map(self): 
        """
        Retrieves the most recent entry from the price history as a map. 
        :return: The latest price if available; otherwise, None.
        """
        if 'price_history_map' in self.game_history and len(self.game_history['price_history_map']) > 0:
            return self.game_history['price_history_map'][-1]
    
    def get_previous_winners(self): 
        """
        Retrieves the most recent entry from the tentative winners history as a ndarray. 
        :return: The latest winners if available; otherwise, None.
        """
        if 'winner_history' in self.game_history and len(self.game_history['winner_history']) > 0:
            return self.game_history['winner_history'][-1]
    
    def get_previous_winners_map(self): 
        """
        Retrieves the most recent entry from the tentative winners history as a map. 
        :return: The latest winners if available; otherwise, None.
        """
        if 'winner_history_map' in self.game_history and len(self.game_history['winner_history_map']) > 0:
            return self.game_history['winner_history_map'][-1]
    
    def get_opp_bid_history(self): 
        """
        Retrieves the history of bids made by the opponent player [AS A NDARRAY].

        :return: A list of opponent bids (np.ndarrays) if available; otherwise, an empty list.
        """
        if 'opp_bid_history' in self.game_history:
            return self.game_history['opp_bid_history']
        else: 
            return []
        
    def get_last_opp_bids(self): 
        """
        Retrieves the most recent entry from the opponent's bid history as a ndarray. 
        :return: The latest opponent bids if available; otherwise, None.
        """
        if 'opp_bid_history' in self.game_history and len(self.game_history['opp_bid_history']) > 0:
            return self.game_history['opp_bid_history'][-1]