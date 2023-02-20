from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, FileField, DateField
from wtforms.validators import InputRequired, Length, EqualTo, Optional

class CreateAccountForm(FlaskForm):
    user_name = StringField('Username', validators = [InputRequired(), Length(min = 6, max = 24)])
    email = StringField('Email', validators = [InputRequired(), Length(min = 8, max = 64)])
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    user_name = StringField('Username', validators = [InputRequired(), Length(min = 6, max = 32)])
    password = PasswordField('Password', validators = [InputRequired()])

class UserProfileForm(FlaskForm):
    user_bio = StringField('Bio', validators = [Optional(), Length(max = 128)])
    first_name = StringField('First name', validators = [Optional(), Length(min = 0, max = 128)])
    middle_name = StringField('Middle name', validators = [Optional(), Length(min = 0, max = 128)])
    last_name = StringField('Last name', validators = [Optional(), Length(min = 0, max = 128)])
    prefix = StringField('Prefix', validators = [Optional(), Length(min = 0, max = 16)])
    suffix = StringField('Suffix', validators = [Optional(), Length(min = 0, max = 16)])
    gender = StringField('Gender', validators = [Optional(), Length(min = 0, max = 16)])
    pronouns = StringField('Pronouns', validators = [Optional(), Length(min = 0, max = 20)])
    address = StringField('Address', validators = [Optional(), Length(min = 0, max = 64)])
    occupation = StringField('Occupation', validators = [Optional(), Length(min = 0, max = 64)])
    city = StringField('City', validators = [Optional(), Length(min = 0, max = 64)])
    country = StringField('Country', validators = [Optional(), Length(min = 0, max = 64)])
    zip = StringField('Zip', validators = [Optional(), Length(min = 0, max = 12)])
    date_of_birth = DateField('Date of Birth', validators = [Optional()])
    
class UserSettingsForm(FlaskForm):
    email = StringField('Change email', validators = [Optional(), Length(min = 8, max = 64)])
    password = PasswordField('New Password', [Optional(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')

class PostForm(FlaskForm):
    text = TextAreaField('Post', validators = [InputRequired(), Length(max = 256)])
    media = FileField('Add media', validators = [FileAllowed(['jpg', 'jpeg', 'png', 'mp4', 'gif'])])