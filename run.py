from app import app
from tornado_server import start_server

if __name__ == "__main__":
    host = app.config.get('APP_RUN_HOST', 'localhost')
    port = app.config.get('APP_RUN_PORT', '5000')
    start_server(host=host, port=port)