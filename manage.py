from app import app, db
from flask_script import Manager
from flask_script.commands import Server
from flask_migrate import Migrate, MigrateCommand
from app.commands import UserCommand


class CustomManager(Manager):
    def add_default_commands(self):
        host = app.config.get('APP_RUN_HOST', 'localhost')
        port = app.config.get('APP_RUN_PORT', '5000')
        self.add_command("runserver", Server(host=host, port=port))
        Manager.add_default_commands(self)

manager = CustomManager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.add_command('user', UserCommand)

if __name__ == '__main__':
    manager.run()
