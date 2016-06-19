from app import app

if __name__ == "__main__":
    host = app.config.get('APP_RUN_HOST', 'localhost')
    port = app.config.get('APP_RUN_PORT', '5000')
    app.run(host=host, port=port)