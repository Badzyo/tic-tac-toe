from tornado.websocket import WebSocketHandler


class GameWSHandler(WebSocketHandler):
    def open(self, game_id):
        pass

    def on_message(self, message):
        pass

    def on_close(self):
        pass
