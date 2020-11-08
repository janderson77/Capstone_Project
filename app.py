import os
from flask import Flask, render_template, request, flash, redirect, session, g, abort, url_for
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from sqlalchemy import desc, asc
from forms import UserAddForm, LoginForm, UploadModForm
from models import db, connect_db, User, Mod, Game
from werkzeug.utils import secure_filename
from pathlib import Path, PurePath
from botocore.exceptions import ClientError

import random
import boto3
import io
import uuid

app = Flask(__name__)
access_key = os.environ.get('access_key')
secret_access_key = os.environ.get('secret_access_key')


client = boto3.client('s3',
                      aws_access_key_id=access_key,
                      aws_secret_access_key=secret_access_key)


ALLOWED_ARCHIVE_EXTENSIONS = {'7z', 'zip', 'zipx', 'rar'}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

CURR_USER_KEY = "curr_user"

MOD_BASE_ID = 'https://mod-page.s3-us-west-1.amazonaws.com/mods/'
IMG_BASE = 'https://mod-page.s3-us-west-1.amazonaws.com/mods/'
PROFILE_IMG_BASE = 'https://mod-page.s3-us-west-1.amazonaws.com/users/'

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///modpage'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'awsonaowhnoawrhnoarw')

app.config['UPLOAD_FOLDER'] = Path('uploads')

# toolbar = DebugToolbarExtension(app)

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


#########################################################################################
# Users Routes
#########################################################################################


@app.route('/users/register', methods=['GET', 'POST'])
def register():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():

        if len(request.files['profile_img'].filename) > 0:
            res = upload_user_image(request)
            profile_image = res['id']
        else:
            profile_image = User.profile_img.default.arg

        try:
            newuser = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                profile_img=profile_image
            )

            db.session.commit()

            user = User.query.filter_by(username=newuser.username).all()

        except IntegrityError as e:
            flash("Username or email already in use", 'danger')
            return render_template('users/register.html', form=form)

        do_login(newuser)

        return redirect(f"/users/{user[0].id}")

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
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have been successfully logged out.", 'success')
    return redirect("/users/login")


@app.route('/users/<int:user_id>')
def showUserProfile(user_id):
    """
    Renders a users profile page with edit permissions only if it's the logged in user's own profile

    Right now it only shows general information. No profile editing has been implemented
    """
    userres = User.query.filter_by(id=user_id).all()
    modsres = Mod.query.filter_by(upload_user_id=user_id).join(Game).all()
    user = userres[0]
    mods = modsres
    totalmods = len(mods)

    if len(userres) < 1:
        abort(404)

    if g.user:
        if g.user.id == user_id:
            return render_template('/users/userprofileown.html', user=user, mods=mods, img_url=IMG_BASE, profile_img=PROFILE_IMG_BASE, totalmods=totalmods)
        else:
            return render_template('/users/userprofile.html', user=user, mods=mods, img_url=IMG_BASE, profile_img=PROFILE_IMG_BASE, totalmods=totalmods)


#########################################################################################
# Games Routes
#########################################################################################


@app.route('/')
def show_all_game_mods():
    """Renders the home page, showing mods for all supported games"""

    mods = Mod.query.group_by(
        Mod.posted_at, Mod.id).all()

    rand_mods = Mod.query.order_by(func.random()).limit(5).all()
    # Returns 5 randomly ordered mods for the random mods section

    feat_mods = Mod.query.order_by(func.random()).limit(4).all()
    # Gets 4 random mods. Will be changed later to get by most likes when that's implemented

    rec_mods = Mod.query.order_by(desc('id')).limit(3).all()
    # Gets most recent mods by querying the highest 3 mod ids

    return render_template('games/index_all_mods.html', mods=mods, img_link=IMG_BASE, rand_mods=rand_mods, rec_mods=rec_mods, feat_mods=feat_mods)


@app.route('/games')
def show_games_list():
    """Show the list of games currently supported for mods"""
    games = Game.query.all()

    return render_template('games/games.html', games=games)


#########################################################################################
# Mods Routes
#########################################################################################


@app.route('/mods/all')
def show_all_mods_list():
    page = request.args.get('page', 1, type=int)
    mods = Mod.query.paginate(page, 5, False)
    img_url = IMG_BASE

    next_url = url_for('show_all_mods_list', page=mods.next_num) \
        if mods.has_next else None
    prev_url = url_for('show_all_mods_list', page=mods.prev_num) \
        if mods.has_prev else None

    return render_template('mods/list_all.html', mods=mods.items, next_url=next_url, prev_url=prev_url, img_url=img_url, page=page)


@app.route('/games/<int:game_id>/mods')
def show_game_mods(game_id):
    """Renders the main mods page for the selected game"""
    mods = Mod.query.filter_by(game_id=game_id).group_by(
        Mod.posted_at, Mod.id).all()

    rand_mods = Mod.query.order_by(func.random()).limit(5).all()
    # Returns 5 randomly ordered mods for the random mods section

    feat_mods = Mod.query.order_by(func.random()).limit(4).all()
    # Gets 4 random mods. Will be changed later to get by most likes when that's implemented

    rec_mods = Mod.query.order_by(desc('id')).limit(3).all()
    # Gets most recent mods by querying the highest 3 mod ids

    game = Game.query.filter_by(id=game_id).all()

    return render_template('games/index.html', mods=mods, img_link=IMG_BASE, rand_mods=rand_mods, rec_mods=rec_mods, feat_mods=feat_mods, game_id=game_id, game=game[0])


@app.route('/games/<int:game_id>/mods/<int:mod_id>', methods=["GET", "POST"])
def show_mod_detials_page(game_id, mod_id):
    """Renders the details page for a mod including download link and images"""

    res = Mod.query.filter_by(id=mod_id).all()
    if len(res) < 1:
        abort(404)

    game = Game.query.filter_by(id=game_id).all()

    user = res[0].user
    mod = res[0]

    filename, file_extension = os.path.splitext(f"{mod.file_id}")
    new_file_name = f"{mod.mod_name}{file_extension}"

    img_link = f"{IMG_BASE}{mod.main_mod_image}"
    modlink = f"{MOD_BASE_ID}{mod.file_id}"
    return render_template('/mods/mod_show.html', user=user, mod=mod, img_link=img_link, modlink=modlink, game_id=game_id, game=game[0], filename=new_file_name)

# @app.route('/games/<int: game_id>/mods/<int: mod_id>/edit')


def allowed_file(filename):
    """Checks that the photos for a mod are of the allowed types"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_archive(filename):
    """Checks that the uploaded mod file is an archive, and is of an allowed type"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_ARCHIVE_EXTENSIONS


@app.route('/games/upload', methods=["GET", "POST"])
def show_mod_upload_page():
    """Renders the mod upload page and handles the upload of mod files"""
    form = UploadModForm()
    form.modgame.choices = [(g.id, g.game_title)
                            for g in Game.query.all()]

    if form.validate_on_submit():

        res = upload_mod_file(request)
        res2 = upload_mod_image(request)

        # Creates a new instance of the Mod class
        newmod = Mod(
            mod_name=form.data['modname'],
            game_id=form.data['modgame'],
            upload_user_id=g.user.id,
            description=form.data['description'],
            requirements=form.data['requirements'],
            installation=form.data['installation'],
            file_id=res['id'],
            main_mod_image=res2['id']
        )

        db.session.add(newmod)
        db.session.commit()

        # queries the new mod so that the user can be redirected to the new mod page
        modinfo = Mod.query.filter_by(file_id=res['id']).all()
        new_mod_game_id = modinfo[0].game_id
        new_mod_id = modinfo[0].id

        return redirect(f'/games/{new_mod_game_id}/mods/{new_mod_id}')

    return render_template('mods/upload.html', form=form)

# @app.route('/games/<int: game_id>/mods/delete')


@app.route('/games/<int:game_id>/mods/list', methods=['GET', 'POST'])
def show_mods_list(game_id):
    """Will show the full list of mods for a given game"""
    page = request.args.get('page', 1, type=int)
    mods = Mod.query.filter_by(game_id=game_id).paginate(page, 5, False)
    game = Game.query.filter_by(id=game_id).all()
    img_url = IMG_BASE

    next_url = url_for('show_mods_list', game_id=game_id, page=mods.next_num) \
        if mods.has_next else None
    prev_url = url_for('show_mods_list', game_id=game_id, page=mods.prev_num) \
        if mods.has_prev else None

    return render_template('mods/list.html', mods=mods.items, next_url=next_url, prev_url=prev_url, img_url=img_url, game=game[0], page=page, game_id=game[0].id)


@app.route('/contact')
def show_contact_page():
    """Renders the contact page"""
    return render_template('contact.html')


##############################################################################
########################    Necessary Functions   ############################
##############################################################################

def upload_mod_file(request):
    """Processes a mod archive for uploading and uploads it"""
    if 'modfile' not in request.files:
        # Checks that there is a file to be uploaded
        flash('No file part', 'danger')
        return redirect('/games/upload')
    files = request.files['modfile']
    if files.filename == '':
        # Checks that the file has a name
        flash('No File Selected', 'danger')
        return redirect('/games/upload')
    if files and allowed_archive(files.filename):
        # Checks that the file is in the list of allowed file types

        filename = secure_filename(files.filename)
        file_ext = Path(files.filename).suffix.lower()
        # Alters the file name so it's not malicious

        filename = str(uuid.uuid1().int)
        filename = f"{filename}{file_ext}"
        files.filename = filename
        # Changes the file name to a randomly generated number to be used as the unique ID

        cwd = Path.cwd()
        f = PurePath(cwd, 'uploads')
        path = Path(f)
        # Finds the uploads file path

        p_obj_path = PurePath(path, filename)
        obj_path = Path(p_obj_path)
        # Sets the path for the file to be saved at

        new_file = files.save(obj_path)

        if obj_path.is_file():
            upload_file_bucket = 'mod-page'
            upload_file_key = 'mods/' + filename
            try:
                file_obj = open(obj_path, 'rb')

                res = client.upload_fileobj(
                    file_obj, upload_file_bucket, upload_file_key)
                file_obj.close()
            except ClientError as e:
                errors = logging.error(e)
                return errors

            mod_file = {'id': filename}
            Path.unlink(obj_path)
            return mod_file
        else:
            flash('Something Went Wrong', 'warning')
            return redirect('/games/upload')


def upload_mod_image(request):
    """Processes a mod image for uploading and uploads it"""
    if 'modimage' not in request.files:
        # Checks that there is a file to be uploaded
        flash('No file part', 'danger')
        return redirect('/games/upload')
    files = request.files['modimage']
    if files.filename == '':
        # Checks that the file has a name
        flash('no selected file', 'danger')
        return redirect('/games/upload')
    if files and allowed_file(files.filename):
        # Checks that the file is in the list of allowed file types
        # files = request.files['modimage']
        file_ext = Path(files.filename).suffix.lower()
        # Alters the file name so it's not malicious

        filename = str(uuid.uuid1().int)
        filename = f"{filename}{file_ext}"
        files.filename = filename
        # Changes the file name to a randomly generated number to be used as the unique ID

        cwd = Path.cwd()
        f = PurePath(cwd, 'uploads')
        path = Path(f)
        # Finds the uploads file path

        p_obj_path = PurePath(path, filename)
        obj_path = Path(p_obj_path)
        # Sets the path for the file to be saved at

        new_file = files.save(obj_path)

        if obj_path.is_file():
            upload_file_bucket = 'mod-page'
            upload_file_key = 'mods/' + filename
            try:
                file_obj = open(obj_path, 'rb')

                res = client.upload_fileobj(
                    file_obj, upload_file_bucket, upload_file_key)
                file_obj.close()
            except ClientError as e:
                errors = logging.error(e)
                return errors
            mod_image = {'id': filename}
            Path.unlink(obj_path)
            return mod_image

        return res


def upload_user_image(request):
    """Processes a user profile image for uploading and uploads it"""
    if 'profile_img' not in request.files:
        # Checks that there is a file to be uploaded
        return
    files = request.files['profile_img']
    if files.filename == '':
        # Checks that the file has a name
        flash('no selected file')
        return redirect('/users/register')
    if files and allowed_file(files.filename):
        # Checks that the file is in the list of allowed file types
        # files = request.files['modimage']
        file_ext = Path(files.filename).suffix.lower()
        # Alters the file name so it's not malicious

        filename = str(uuid.uuid1().int)
        filename = f"{filename}{file_ext}"
        files.filename = filename
        # Changes the file name to a randomly generated number to be used as the unique ID

        cwd = Path.cwd()
        f = PurePath(cwd, 'uploads')
        path = Path(f)
        # Finds the uploads file path

        p_obj_path = PurePath(path, filename)
        obj_path = Path(p_obj_path)
        # Sets the path for the file to be saved at

        new_file = files.save(obj_path)

        if obj_path.is_file():
            upload_file_bucket = 'mod-page'
            upload_file_key = 'users/' + filename
            try:
                file_obj = open(obj_path, 'rb')

                res = client.upload_fileobj(
                    file_obj, upload_file_bucket, upload_file_key)
                file_obj.close()
            except ClientError as e:
                errors = logging.error(e)
                return errors
            user_image = {'id': filename}
            Path.unlink(obj_path)
            return user_image

        return res


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
