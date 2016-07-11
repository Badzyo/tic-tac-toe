from flask import url_for
from wtforms.validators import ValidationError
from app.models import User


class UniqueUserNameValidator:
    """
    Raises an error if user with entered username is already exists
    """
    def __init__(self, message=None):
        if message:
            self.message = message
        else:
            self.message = "The user '{}' is already exists. Please, choose another name."

    def __call__(self, form, field):
        name = field.data
        user_found = User.query.filter_by(username=name).count()
        if user_found > 0:
            message = self.message
            raise ValidationError(message.format(name))


class UniqueEmailValidator:
    """
    Raises an error if user with entered email is already exists
    """
    def __init__(self, message=None):
        if message:
            self.message = message
        else:
            self.message = """
                           A user with this e-mail is already exists. <br>
                           Please, specify another e-mail or go to <a href='{}'>Login page</a>.
                           """

    def __call__(self, form, field):
        email = field.data
        emails_found = User.query.filter_by(email=email).count()
        if emails_found > 0:
            message = self.message
            raise ValidationError(message.format(url_for('login')))


class GameCreationFormSizeValidator:
    """
    Raises an error if a size field less then rule field (win length)
    """
    def __init__(self):
        self.win_length_filedname = 'rule'

    def __call__(self, form, field):
        size = field.data
        win_length = form[self.win_length_filedname].data
        if size < win_length:
            self.message = "Grid size can't be less then win condition length"
            raise ValidationError(self.message)

        if win_length == 3 and size > 3:
            self.message = "Obviously a winning situation for first player. Grid size > 3 and win condition is 3 in row"
            raise ValidationError(self.message)
