from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, FileField
from wtforms.validators import InputRequired, Length, EqualTo, Optional

class CreateAccountForm(FlaskForm):
    user_name = StringField('Username', validators = [InputRequired(), Length(min = 6, max = 32)])
    email = StringField('Email', validators = [InputRequired(), Length(min = 8, max = 64)])
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    user_name = StringField('Username', validators = [InputRequired(), Length(min = 6, max = 32)])
    password = PasswordField('Password', validators = [InputRequired()])

class UserProfileForm(FlaskForm):
    user_bio = StringField('Enter user bio:', validators = [Optional(), Length(min = 0, max = 128)])

class UserSettingsForm(FlaskForm):
    email = StringField('Change email', validators = [Optional(), Length(min = 8, max = 64)])
    password = PasswordField('New Password', [Optional(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')

class PostForm(FlaskForm):
    text = TextAreaField('Post', validators = [InputRequired(), Length(max = 256)])
    media = FileField('Add media', validators = [FileAllowed(['jpg', 'jpeg', 'png', 'mp4', 'gif'])])