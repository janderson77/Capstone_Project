from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Users in the system"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.Text, nullable=False, unique=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False, unique=True)

    profile_img = db.Column(
        db.Text, default='/static/images/default_profile.jpg')

    mod = db.relationship('Mod')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, profile_img):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            profile_img=profile_img,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Mod(db.Model):

    __tablename__ = 'mods'

    id = db.Column(db.Integer, primary_key=True)

    mod_name = db.Column(db.Text, nullable=False)

    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

    game = db.relationship('Game')

    upload_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User')

    posted_at = db.Column(db.Date(), nullable=False,
                          default=datetime.now())

    description = db.Column(db.Text)

    requirements = db.Column(db.Text)

    installation = db.Column(db.Text)

    file_id = db.Column(db.Text, nullable=False)

    main_mod_image = db.Column(
        db.Text, nullable=False, default='default_mod_image.jpg')

    sub_images = db.relationship('SubImages')

    def __repr__(self):
        return f"<Mod #{self.id}: {self.mod_name}, uploaded by: {self.upload_user_id}>"


class SubImages(db.Model):

    __tablename__ = 'subimages'

    id = db.Column(db.Integer, primary_key=True)

    mod_id = db.Column(db.Integer, db.ForeignKey('mods.id'))

    mod = db.relationship('Mod')

    image_url = db.Column(db.Text, nullable=False)


class Game(db.Model):
    """
        File extenstion for the game image is to be left off by default to allow for dinamic image sizes to be used.

        Image naming must follow the convention of "game_name" with the varying sizes having an underscore before the size declaration, i.e. "_sm"

        When calling the image in a template, do not forget to include the extension (jpg should be used) after the closing curly braces

        Note: This rule does not apply to the Mods class
    """
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)

    game_title = db.Column(db.Text, nullable=False, unique=True)

    game_image = db.Column(db.Text, nullable=False,
                           default='/static/images/default_mod_image')

    game_developer = db.Column(db.Text)

    game_genre = db.Column(db.Text,)

    release_year = db.Column(db.Text)

    description = db.Column(db.Text)

    mod = db.relationship('Mod')

    def __repr__(self):
        return f"<Game #{self.id}: {self.game_title}, made by: {self.game_developer}, released on {self.release_year}>"
