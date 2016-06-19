from app import db
from app.models import User
from flask_script import Manager

user_command = Manager(usage='Add a new user')


@user_command.option('--admin', dest='admin', default=False, help='Admin flag')
def add(admin=False):
    """
    This is the manager command to add a new user to database.
    Use '--admin=True' option to make an Administrator user (not implemented yet)
    """
    if admin:
        raise NotImplementedError("Admin creation is not implemented yet.")

    name = input("Enter username: ")
    email = input("Enter user e-mail: ")
    password = input("Set password: ")
    user = User(username=name, password=password, email=email)
    db.session.add(user)
    db.session.commit()
    print("user added!")
