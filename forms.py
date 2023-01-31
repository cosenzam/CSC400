from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, EqualTo

class CreateAccountForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired(), Length(min = 6, max = 32)])
    email = StringField('Email', validators = [InputRequired(), Length(min = 8, max = 64)])
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired(), Length(min = 6, max = 32)])
    password = PasswordField('Password', validators = [InputRequired()])