from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import exc
from flask_login import UserMixin
from app import app, db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(20))
    email = db.Column('email', db.String(50), unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime, default=datetime.utcnow())
    games = db.relationship('GameUser', lazy='dynamic')

    def __init__(self, username, password, email, registered=None):
        super().__init__()
        self.username = username
        self.email = email
        self.set_password(password)
        if registered:
            self.registered_on = registered

    def set_password(self, password):
        self.password = generate_password_hash(password, method=app.config.get('PASSWORD_HASH_ALGORITHM', 'sha256'))

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def get_authenticated_user(cls, username, password):
        """ Returns User object if it's found by username and password is correct.
        Otherwise returns None
        """
        user = cls.get_user_by_name(username)
        try:
            if user.check_password(password):
                return user
        except AttributeError:
            pass
        return None

    @classmethod
    def get_user_by_name(cls, username):
        """ Returns User object by username.
            If user is not found, returns None
        """
        try:
            return cls.query.filter_by(username=username).first()
        except exc.NoResultFound:
            return None

    @classmethod
    def get_user_by_id(cls, user_id):
        """ Returns User object by ID.
            If user is not found, returns None
        """
        try:
            return cls.query.filter_by(id=user_id).first()
        except exc.NoResultFound:
            return None

    @property
    def current_game(self):
        """
        Returns user's current game, or None
        """
        # TODO: come up with a better solution, using join
        user_games = self.games
        for user_game in user_games:
            if user_game.game.state != Game.game_state['finished']:
                return user_game.game
        return None

    def __repr__(self):
        return '{} <{}>'.format(self.username, self.email)


class Game(db.Model):
    """
    Model of a Game-entity
    """
    game_state = {'waiting_for_players': 0,
                  'in_progress': 1,
                  'finished': 2}

    game_result = {'draw': 0,
                   'player_one_win': 1,
                   'player_two_win': 2}

    __tablename__ = 'games'
    id = db.Column('game_id', db.Integer, primary_key=True)
    field_size = db.Column(db.Integer)
    win_length = db.Column(db.Integer)
    state = db.Column(db.Integer, default=game_state['waiting_for_players'])
    result = db.Column(db.Integer)
    users = db.relationship('GameUser', lazy='dynamic')
    moves = db.relationship('GameMove', backref='game', lazy='dynamic')

    def __repr__(self):
        return 'ID: {}, State: {}, Result: {}>'.format(self.id, self.state, self.result)


class GameUser(db.Model):
    """
    Intermediary model for Games-to-Users many-to-many relation
    """
    user_game_role = {'player_one': 1,
                      'player_two': 2}

    __tablename__ = 'game_users'
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    user_role = db.Column(db.Integer)
    game = db.relationship('Game')
    user = db.relationship('User')

    def __repr__(self):
        return 'game_id: {}, user_id: {}, user_role: {}'.format(self.game_id, self.user_id, self.user_role)


class GameMove(db.Model):
    """
    Model of player's move in a game
    """
    move_type = {'player_one': 1,
                 'player_two': 2}

    __tablename__ = 'moves'
    id = db.Column('move_id', db.Integer, primary_key=True)
    ordinal_number = db.Column(db.Integer)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'))
    player = db.Column(db.Integer)
