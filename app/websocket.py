import json
import datetime
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from app.game import ActiveGameHandler


class GameWSHandler(WebSocketHandler):
    _active_games = dict()

    def __init__(self, application, request, **kwargs):
        WebSocketHandler.__init__(self, application, request, **kwargs)
        self.active_game = None
        self.player_number = None
        self.ping_interval = 10
        self.message_handlers = {
            'move': self.handle_move,
            'chat': self.handle_chat,
            'flee': self.handle_flee
        }

    def _ping(self):
        """
        Periodically ping connection to keep it alive
        """
        try:
            self.ping(b'ping')
            IOLoop.instance().add_timeout(datetime.timedelta(seconds=self.ping_interval), self._ping)
        except WebSocketClosedError as e:
            pass

    def open(self, game_id, player_number):
        self.player_number = int(player_number)
        self.active_game = self._get_active_game(game_id)

        # add current user to online users in active game
        self.active_game.connect_user(self.player_number, self)

    def on_message(self, message):
        msg = json.loads(message)
        try:
            msg_type = msg['message']
        except KeyError:
            return
        handle_message = self.message_handlers.get(msg_type, None)
        if handle_message:
            handle_message(msg)

    def on_close(self):
        # remove player from online players in active game
        self.active_game.disconnect_user(self.player_number)

        # remove current active game from the list if all players and spectators are disconnected
        if self.active_game.is_empty:
            GameWSHandler._remove_active_game(self.active_game.id)


    @classmethod
    def _get_active_game(cls, game_id):
        try:
            active_game = cls._active_games[game_id]
        except KeyError:
            active_game = ActiveGameHandler(game_id=game_id)
            cls._active_games[game_id] = active_game
        return active_game

    @classmethod
    def _remove_active_game(cls, game_id):
        cls._active_games.pop(game_id, None)

    def handle_move(self, message):
        self.active_game.apply_move(self.player_number, message['cell'])

    def handle_chat(self, message):
        self.active_game.send_chat_message(self.player_number, message['text'])

    def handle_flee(self, message):
        self.active_game.flee(self.player_number)
