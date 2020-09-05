from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    profile_img = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UploadModForm(FlaskForm):
    modname = StringField('The name of your Mod', validators=[DataRequired()])
    modgame = SelectField('The Game the mod is for')
    description = StringField('(Optional) Description for your Mod')
    requirements = StringField('(Optional) Requirements for your Mod')
    installation = StringField(
        '(Optional) Installation Instructions for your Mod')
    modfile = FileField('Mod File Archive (7z, zip, zipx, rar Only)')
    modimage = FileField('Main Mod Image(png, jpg, jpeg, gif)')
