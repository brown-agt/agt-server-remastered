from collections import defaultdict
class GameReport(): 
    def __init__(self) -> None:
        self.game_history = defaultdict(lambda: [])
        
    def __str__(self) -> str:
        return f"Game Report: \n {self.game_history}"
    
    def __repr__(self) -> str:
        return self.__str__()

    def get_game_report_as_dict(self): 
        return self.game_history
    
    def get_action_history(self):
        if 'my_action_history' in self.game_history:
            return self.game_history['my_action_history']
        else: 
            return []

    def get_util_history(self):
        if 'my_utils_history' in self.game_history:
            return self.game_history['my_utils_history']
        else: 
            return []


    def get_opp_action_history(self):
        if 'opp_action_history' in self.game_history:
            return self.game_history['opp_action_history']
        else: 
            return []

    def get_opp1_action_history(self): 
        if "opp1_action_history" in self.game_history:
            return self.game_history['opp1_action_history']
        else: 
            return []

    
    def get_opp2_action_history(self): 
        if "opp2_action_history" in self.game_history:
            return self.game_history['opp2_action_history']
        else: 
            return []

    def get_opp_util_history(self):
        if 'opp_utils_history' in self.game_history:
            return self.game_history['opp_utils_history']
        else: 
            return []
    
    def get_opp1_util_history(self): 
        if "opp1_utils_history" in self.game_history:
            return self.game_history['opp1_utils_history']
        else: 
            return []
    
    def get_opp2_util_history(self): 
        if "opp2_utils_history" in self.game_history:
            return self.game_history['opp2_utils_history']
        else: 
            return []

    def get_last_action(self):
        if 'my_action_history' in self.game_history and len(self.game_history['my_action_history']) > 0:
            return self.game_history['my_action_history'][-1]
        
    def get_last_util(self):
        if 'my_utils_history' in self.game_history and len(self.game_history['my_utils_history']) > 0:
            return self.game_history['my_utils_history'][-1]

    def get_opp_last_action(self):
        if 'opp_action_history' in self.game_history and len(self.game_history['opp_action_history']) > 0:
            return self.game_history['opp_action_history'][-1]

    def get_opp1_last_action(self):
        if 'opp1_action_history' in self.game_history and len(self.game_history['opp1_action_history']) > 0:
            return self.game_history['opp1_action_history'][-1]
    
    def get_opp2_last_action(self):
        if 'opp2_action_history' in self.game_history and len(self.game_history['opp2_action_history']) > 0:
            return self.game_history['opp2_action_history'][-1]
    
    def get_opp_last_util(self):
        if 'opp_utils_history' in self.game_history and len(self.game_history['opp_utils_history']) > 0:
            return self.game_history['opp_utils_history'][-1]
    
    def get_opp1_last_util(self):
        if 'opp1_utils_history' in self.game_history and len(self.game_history['opp1_utils_history']) > 0:
            return self.game_history['opp1_utils_history'][-1]
    
    def get_opp2_last_util(self):
        if 'opp2_utils_history' in self.game_history and len(self.game_history['opp2_utils_history']) > 0:
            return self.game_history['opp2_utils_history'][-1]
    
    def get_mood_history(self):
        if 'mood_history' in self.game_history:
            return self.game_history['mood_history']
        else: 
            return []
    
    def get_last_mood(self):
        if 'mood_history' in self.game_history and len(self.game_history['mood_history']) > 0:
            return self.game_history['mood_history'][-1]
    
    