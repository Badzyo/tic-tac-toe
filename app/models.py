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

    def __repr__(self):
        return '{} <{}>'.format(self.username, self.email)

