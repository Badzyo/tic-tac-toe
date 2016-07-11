from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from app.validators import UniqueUserNameValidator, UniqueEmailValidator, GameCreationFormSizeValidator


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


class NewGameForm(Form):
    sizes = [(3, '3x3'),
             (4, '4x4'),
             (5, '5x5'),
             (6, '6x6'),
             (7, '7x7'),
             (8, '8x8'),
             (9, '9x9'),
             (10, '10x10')]

    rules = [(3, '3 in row'),
             (4, '4 in row'),
             (5, '5 in row')]
    rule = SelectField('Winning rule', default=3, choices=rules, coerce=int)
    size = SelectField('Size of the game field', default=3, choices=sizes, coerce=int,
                       validators=[GameCreationFormSizeValidator()])
