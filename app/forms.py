from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from app.validators import UniqueUserNameValidator, UniqueEmailValidator


class LoginForm(Form):
    username = StringField('Your name', validators=[Length(min=3, max=20)])
    password = PasswordField('Your password', validators=[DataRequired()])


class RegisterForm(Form):
    username = StringField('Your name', validators=[Length(min=3, max=20), UniqueUserNameValidator()])
    email = StringField('E-mail', validators=[Email(), UniqueEmailValidator()])
    password = PasswordField('Choose password',
                             validators=[Length(min=3, max=20),
                                         EqualTo("password_check", message="Passwords don't match")])
    password_check = PasswordField('Repeat password', validators=[Length(min=3, max=20)])
