from tornado.wsgi import WSGIContainer
from tornado.web import Application, FallbackHandler
from tornado.ioloop import IOLoop
from app.websocket import GameWSHandler
from app import app


def start_server(host='localhost', port=5000):
    wsgi_app = WSGIContainer(app)

    server = Application([
        (r'/ws/game/(?P<game_id>\d+)/(?P<player_number>\d+)', GameWSHandler),
        (r'.*', FallbackHandler, dict(fallback=wsgi_app)),
    ])
    server.listen(port=port, address=host)
    IOLoop.instance().start()
