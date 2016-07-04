from flask import Flask
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import LoginManager
from app.mixins import GuestUserMixin

app = Flask(__name__)
app.config.from_object('config')


engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db_scoped_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_scoped_session.query_property(query_cls=BaseQuery)

db = SQLAlchemy(app)
db.session = db_scoped_session
db.Model = Base


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = GuestUserMixin

from app import views, models
