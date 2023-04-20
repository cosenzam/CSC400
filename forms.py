from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, DateField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, Optional


class CreateAccountForm(FlaskForm):
    user_name = StringField('Username', validators = [InputRequired(), Length(min = 6, max = 24)])
    email = StringField('Email', validators = [InputRequired(), Length(min = 8, max = 64)])
    password = PasswordField('Password', validators = [InputRequired()])
    confirm  = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    user_name = StringField('Username', validators = [InputRequired(), Length(min = 6, max = 32)])
    password = PasswordField('Password', validators = [InputRequired()])

class UserProfileForm(FlaskForm):
    user_bio = StringField('Bio', validators = [Optional(), Length(max = 128)])
    first_name = StringField('First name', validators = [Optional(), Length(min = 0, max = 128)])
    middle_name = StringField('Middle name', validators = [Optional(), Length(min = 0, max = 128)])
    last_name = StringField('Last name', validators = [Optional(), Length(min = 0, max = 128)])
    pronouns = StringField('Pronouns', validators = [Optional(), Length(min = 0, max = 20)])
    address = StringField('Address', validators = [Optional(), Length(min = 0, max = 64)])
    occupation = StringField('Occupation', validators = [Optional(), Length(min = 0, max = 64)])
    location = StringField('Location', validators = [Optional(), Length(min = 0, max = 64)])
    date_of_birth = DateField('Date of Birth', validators = [Optional()])
    profile_picture = FileField('Upload PFP', validators = [Optional(), FileAllowed(['jpg', 'jpeg', 'png'])])

class UserSettingsForm(FlaskForm):
    email = StringField('New email', validators = [Optional(), Length(min = 8, max = 64)])
    current_password = PasswordField('Current Password')
    password = PasswordField('New Password')
    confirm  = PasswordField('Repeat Password')

class PostForm(FlaskForm):
    text = TextAreaField('Write a Post', validators = [Optional(), Length(max = 256)])
    media = FileField('Add Media', validators = [Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4'])])

class RecoveryForm(FlaskForm):
    email = StringField('Email', validators = [InputRequired(), Length(min = 8, max = 64)])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators = [InputRequired()])
    confirm  = PasswordField('Repeat Password')

class SearchForm(FlaskForm):
    search = StringField('Username', validators = [Optional(), Length(max = 256)])
    submit = SubmitField("Submit")