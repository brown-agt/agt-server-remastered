class Game:
    def __init__(self, num_rounds, player_data, player_types, permissions_map, game_turn_timeout, game_name, invalid_move_penalty):
        if game_name != None:
            self.game_name = game_name
        else:
            self.game_name = "Please give the Game a name"
        self.num_rounds = num_rounds
        self.player_data = player_data
        self.player_types = player_types
        self.permissions_map = permissions_map
        self.invalid_move_penalty = invalid_move_penalty
        self.game_reports = {}
        for data in self.player_data:
            data['client'].settimeout(game_turn_timeout)

    def run_game(self):
        raise NotImplementedError
