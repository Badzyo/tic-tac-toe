from tornado.websocket import WebSocketHandler


class GameWSHandler(WebSocketHandler):
    _active_games = {}

    def __init__(self, application, request, **kwargs):
        WebSocketHandler.__init__(self, application, request, **kwargs)
        self.active_game = None
        self.player_number = None

    def open(self, game_id):
        self.active_game = GameWSHandler._get_active_game(game_id)

    def on_message(self, message):
        pass

    def on_close(self):
        GameWSHandler._remove_active_game(self.active_game)

    @classmethod
    def _get_active_game(cls, game_id):
        try:
            active_game = cls._active_games[game_id]
        except KeyError:
            active_game = game_id
            cls._active_games[game_id] = active_game
        return active_game

    @classmethod
    def _remove_active_game(cls, game_id):
        cls._active_games.pop(game_id, None)