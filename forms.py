from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SelectField, TextAreaField
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
    modname = StringField('The Name Of Your Mod', validators=[
                          DataRequired()], description="Super Awesome and Immersive Mod")
    modgame = SelectField('The Game The Mod Is For')
    description = TextAreaField(
        'Description For Your Mod', description="(Optional)")
    requirements = TextAreaField(
        'Requirements For Your Mod', description="(Optional)")
    installation = TextAreaField(
        'Installation Instructions For Your Mod', description="(Optional)")
    modfile = FileField('Mod File Archive (7z, zip, zipx, rar)',
                        validators=[
                            FileRequired(), FileAllowed(
                                ['7z', 'zip', 'zipx', 'rar'], 'Archives Only!')
                        ],
                        render_kw={"accept": ".7z, .zip, .zipx, .rar"}
                        )
    modimage = FileField('Main Mod Image (png, jpg, jpeg, gif)',
                         validators=[
                             FileAllowed(['png', 'jpg', 'jpeg', 'gif'], "Images Only!")],
                         render_kw={"accept": ".png, .jpg, .jpeg, .gif"}
                         )
