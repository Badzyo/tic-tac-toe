from tornado.websocket import WebSocketHandler
from app.game import ActiveGameHandler


class GameWSHandler(WebSocketHandler):
    _active_games = dict()

    def __init__(self, application, request, **kwargs):
        WebSocketHandler.__init__(self, application, request, **kwargs)
        self.active_game = None
        self.player_number = None

    def open(self, game_id, player_number):
        self.player_number = int(player_number)
        self.active_game = self._get_active_game(game_id)

        # add current user to online users in active game
        self.active_game.connect_user(self.player_number, self)

    def on_message(self, message):
        print(message)  # for debug

    def on_close(self):
        # remove player from online players in active game
        self.active_game.disconnect_user(self.player_number)

        # remove current active game from the list if all players and spectators are disconnected
        if self.active_game.is_empty:
            GameWSHandler._remove_active_game(self.active_game.id)

    def _get_active_game(self, game_id):
        try:
            active_game = GameWSHandler._active_games[game_id]
        except KeyError:
            active_game = ActiveGameHandler(game_id=game_id, player_number=self.player_number, socket=self)
            GameWSHandler._active_games[game_id] = active_game
        return active_game

    @classmethod
    def _remove_active_game(cls, game_id):
        cls._active_games.pop(game_id, None)