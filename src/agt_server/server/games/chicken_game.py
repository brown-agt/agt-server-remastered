from agt_server.server.games.complete_2x2_matrix_game import Complete2by2MatrixGame


class ChickenGame(Complete2by2MatrixGame):
    def __init__(self, server_config, num_rounds=1000, player_data=[], player_types=[], permissions_map={}, game_kick_timeout=60, game_name=None, invalid_move_penalty=0, timeout_tolerance = 10):
        super().__init__(num_rounds, player_data,
                         player_types, permissions_map, game_kick_timeout, game_name, invalid_move_penalty, timeout_tolerance)
        self.server_config = server_config
        self.valid_actions = [0, 1]
        self.utils = [[(0, 0), (-1, 1)],
                      [(1, -1), (-5, -5)]]
