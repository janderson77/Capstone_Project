import os
from flask import Flask, render_template, request, flash, redirect, session, g, abort, url_for
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, LoginForm, UploadModForm
from models import db, connect_db, User, Mod, Game
from werkzeug.utils import secure_filename
from Google import Create_Service
from googleapiclient.http import MediaFileUpload, DEFAULT_CHUNK_SIZE

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///modpage'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def show_home_page():
    if g.user:

        return render_template('index.html')

    else:
        return render_template('index-anon.html')


@app.route('/users/register', methods=['GET', 'POST'])
def register():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                profile_img=form.profile_img.data or User.profile_img.default.arg,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/register.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/register.html', form=form)


@app.route('/users/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

# @app.route('/users/<int:user_id>')


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have been successfully logged out.", 'success')
    return redirect("/login")


@app.route('/games')
def show_games_list():
    return render_template('games/games.html')


@app.route('/contact')
def show_contact_page():
    """Renders the contact page"""
    return render_template('contact.html')

# @app.route('/games/<int: game_id>/mods')
# @app.route('/games/<int: game_id>/mods/<int: mod_id>')
# @app.route('/games/<int: game_id>/mods/<int: mod_id>/edit')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/games/upload', methods=["GET", "POST"])
def show_mod_upload_page():
    form = UploadModForm()
    form.modgame.choices = [(g.id, g.game_title)
                            for g in Game.query.all()]

    if form.validate_on_submit():
        if 'modfile' not in request.files:
            flash('No file part')
            return redirect('/games/upload')
        upfile = request.files['modfile']
        if upfile.filename == '':
            flash('no selected file')
            return redirect('/games/upload')
        if upfile and allowed_file(upfile.filename):
            filename = secure_filename(upfile.filename)
            upfile.save(os.path.join('/tmp', filename))

            metadata = {'name': filename}

            media = MediaFileUpload('/tmp/{0}'.format(filename), mimetype=upfile.mimetype,
                                    chunksize=DEFAULT_CHUNK_SIZE, resumable=False)

            res = service.files().create(body=metadata, media_body=media).execute()

            newmod = Mod(
                drive_id=res['id'],
                mod_name=form.data['modname'],
                game_id=form.data['modgame'],
                upload_user_id=g.user.id,
                description=form.data['description'],
                requirements=form.data['requirements'],
                installation=form.data['installation']
            )

            db.session.add(newmod)
            db.session.commit()

            modinfo = Mod.query.filter_by(drive_id=res['id']).all()
            new_mod_game_id = modinfo[0].game_id
            new_mod_id = modinfo[0].id
            # import pdb
            # pdb.set_trace()
            return redirect(f'/games/{new_mod_game_id}/mods/{new_mod_id}')
        return redirect('/')
    return render_template('mods/upload.html', form=form)

# @app.route('/games/<int: game_id>/mods/edit')
# @app.route('/games/<int: game_id>/mods/delete')
# @app.route('/games/<int: game_id>/mods/search')


@ app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


@ app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
