from flask import Flask, redirect, url_for, render_template, session, flash, request
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import timedelta, datetime
from passlib.hash import sha256_crypt
from forms import CreateAccountForm, LoginForm, UserProfileForm, UserSettingsForm, PostForm, SearchForm
from connect import db_connect #connect.py method that handles all connections, returns engine.
from models import Base, User, Post, Interaction, Media, MediaCollection
from email_validator import validate_email, EmailNotValidError
import models
from models import insert_user, get_user, exists_user, insert_interaction, insert_post, exists_post
import os, os.path
from werkzeug.utils import secure_filename

#app settings
app = Flask(__name__)
app.secret_key = "asdf"
app.permanent_session_lifetime = timedelta(days = 7) # session length
app.config['UPLOAD_FOLDER'] = 'static/images'


#data base connections
engine = db_connect()
Session_MySQLdb = sessionmaker(engine)
db_session = Session_MySQLdb()

models.session = db_session

# Base.metadata.drop_all(engine, checkfirst=False)

# Create all database tables in models.pygi
Base.metadata.create_all(engine)

# Find if email exists in DB and is a valid format
def valid_email(email):

    exists = exists_user(email=email)
    if exists:
        flash("Email already in use", "info")
        return False

    try:
        validation = validate_email(email)
        email = validation.email
    except EmailNotValidError as errorMsg:
        print(str(errorMsg))
        flash("Email not valid", "info")
        return False

    return True

# Verifies password requirements | must contain at least 1 number and 1 letter
def valid_pass(password, confirm_password):
    has_letters = any(c.isalpha() for c in password)
    has_numbers = any(i.isdigit() for i in password)

    if password == confirm_password:
        pass
    else:
        flash("Passwords must match!")
        return False

    if has_letters and has_numbers and len(password) >= 8:
        return True
    else:
        flash("Passwords must be at least 8 characters in length and contain one number and one letter")
        return False

# Days since post was created
def getPostRecency(post):
    d1 = datetime.now()
    d2 = post.timestamp

    delta = d1 - d2
    recency_tuple = (delta.seconds, delta.seconds//60, delta.seconds//3600, delta.days)

    return recency_tuple

# Show time since post was created if days <= 7, otherwise show locally formatted date
# recency_typle = (seconds, mins, hours, days)
def postDateFormat(post, recency_tuple):
    seconds = recency_tuple[0]
    minutes = recency_tuple[1]
    hours = recency_tuple[2]
    days = recency_tuple[3]
    #print(seconds, minutes, hours, days)

    if days < 1:
        if hours < 1:
            if minutes < 1:
                return str(seconds)+"s"
            else:
                return str(minutes)+"m"
        else:
            return str(hours)+"h"
    elif days <= 7:
        return str(days)+"d"
    else:
        return post.timestamp.strftime("%x")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view")
def view():
    return render_template("view.html", values = db_session.query(User).all())

@app.route("/create_account/", methods=["POST", "GET"])
def create_account():
    form = CreateAccountForm()
    if request.method == "POST" and form.validate_on_submit():
        session.permanent = True
        user_name = form.user_name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm.data
        if exists_user(user_name=user_name):
            flash("Username already exists", "info")
            return redirect(url_for("create_account"))
        elif not valid_email(email):
            return redirect(url_for("create_account"))
        elif not valid_pass(password, confirm_password):
            return redirect(url_for("create_account"))
        else: 
            session["user"] = user_name # add user to session
            hashed_password = sha256_crypt.hash(password)

            #insert_user() requires these three, and only these.
            #you can use user.update_user() for other fields.
            user = insert_user(
                user_name = user_name, 
                email = email, 
                password = hashed_password
                )
            
            #gonna add current user's user_id to session
            session["user_id"] = int(user.id)

            return redirect(url_for("user", dynamic_user = session["user"]))
    else:
        if "user" in session:
            #flash("Already logged in", "info")
            return redirect(url_for("user", dynamic_user = session["user"]))
    return render_template("create_account.html", form = form)
    
    

@app.route("/login/", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data

        #exists_user() returns simple boolean
        if exists_user(user_name=user_name): 
            user = get_user(user_name=user_name)
            hashed_password = user.password
            if sha256_crypt.verify(password, hashed_password):
                session.permanent = True
                session["user"] = user_name
                session["user_id"] = user.id
                #flash("Login Success", "info")
                return redirect(url_for("user", dynamic_user = session["user"]))
            else:
                flash("Incorrect Password", "info")
                return redirect(url_for("login"))
        else:
            flash("User not found", "info")
            return redirect(url_for("login"))
    else:
        if "user" in session:
            #flash("Already Logged in", "info")
            return redirect(url_for("user", dynamic_user = session["user"]))
    return render_template("login.html", form = form)

@app.route("/logout/")
def logout():
    if "user" in session:
        user = session["user"]
        session.pop("user", None)
        flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/user/<dynamic_user>/", methods=["POST", "GET"])
def user(dynamic_user):
    # If page is the logged in user's, give appropriate permissions
    if "user" in session and dynamic_user == session["user"]:
        form = PostForm()
        user_id = session["user_id"]

        #kept profile variable name the same for now
        profile = get_user(id=user_id) #user object

        #a user object has a list of post objects made by that user
        postings = profile.posts 
        #files = media.file_path

        if request.method == "POST" and form.validate_on_submit():
            
            text = form.text.data
            media = form.media.data

            if media is not None:
                filename = secure_filename(media.filename)
                media.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            if media == "" and text == "":
                flash("Text and Media Fields cannot both be blank!")
                return redirect(url_for("create_post"))
            
            else:

                #insert_post() returns a post object
                post = insert_post(profile, text)
                flash("Post Created!")
                return redirect(url_for("user", dynamic_user = session["user"]))

        return render_template("user.html", profile = profile, dynamic_user = dynamic_user, posts = postings, form = form, 
        getPostRecency = getPostRecency, postDateFormat = postDateFormat)
    # If page is not the logged in user's
    else:
        if exists_user(user_name=dynamic_user):
            profile = get_user(user_name=dynamic_user)

            postings = profile.posts

            #for post in postings:
            #    print(postDateFormat(post, getDays(post)))

            return render_template("user.html", profile = profile, dynamic_user = dynamic_user, posts = postings, 
            getPostRecency = getPostRecency, postDateFormat = postDateFormat)
        else:
            flash("User not found", "info")
            return redirect(url_for("home"))

@app.route("/edit_profile/", methods=["POST", "GET"])
def edit_profile():
    if "user" in session:
        user = session["user"]
        user_id = session["user_id"]
        form = UserProfileForm()

        profile = get_user(id=user_id)

        if request.method == "GET":
            if profile.bio != "NULL":
                form.user_bio.data = profile.bio
            if profile.first_name != "NULL":
                form.first_name.data = profile.first_name
            if profile.middle_name != "NULL":
                form.middle_name.data = profile.middle_name
            if profile.last_name != "NULL":
                form.last_name.data = profile.last_name
            if profile.pronouns != "NULL":
                form.pronouns.data = profile.pronouns
            if profile.occupation != "NULL":
                form.occupation.data = profile.occupation
            if profile.location != "NULL":
                form.location.data = profile.location
            if profile.date_of_birth != "NULL":
                form.date_of_birth.data = profile.date_of_birth
            '''
            if profile.profile_picture_media_id != "NULL":
                form.profile_picture_media_id.data = profile.profile_picture_media_id
                filename = secure_filename(profile.profile_picture_media_id.filename)
                profile.profile_picture_media_id.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            '''
        if request.method == "POST" and form.validate_on_submit():

            #profile is a user object, User.update() take kwargs for each of its fields.
            profile.update(
                bio = form.user_bio.data,
                first_name = form.first_name.data,
                middle_name = form.middle_name.data,
                last_name = form.last_name.data,
                pronouns = form.pronouns.data,
                occupation = form.occupation.data,
                location = form.location.data,
                date_of_birth = form.date_of_birth.data
                #profile_picture_media_id = form.profile_picture_media_id.data
            )

            flash("Your profile has been updated", "info")
            return redirect(url_for("edit_profile"))

        return render_template("edit_profile.html", user_name = user, form = form)
    else:
        flash("You must be logged in to edit your profile", "info")
        return redirect(url_for("login"))

@app.route("/settings/", methods=["POST","GET"])
def user_settings():
    if "user" in session:
        user_name = session["user"]
        form = UserSettingsForm()
        user = get_user(user_name=user_name)

        if request.method == "GET":
            form.email.data = user.email

        if request.method == "POST" and form.validate_on_submit():
            current_password = form.current_password.data
            new_password = form.password.data
            confirm_password = form.confirm.data
            email = form.email.data

            if email:
                if email == user.email:
                    flash("New email cannot be current email", "info")
                elif valid_email(email):
                    user.update(email = email)
                    flash("Email saved", "info")

            if current_password:
                if sha256_crypt.verify(current_password, user.password):
                    if sha256_crypt.verify(new_password, user.password):
                        flash("New password cannot be old password", "info")
                    elif new_password and valid_pass(new_password, confirm_password):
                        hashed_password = sha256_crypt.hash(new_password)
                        user.update(password = hashed_password)
                        flash("Password sucessfully changed", "info")
                else:
                    flash("Incorrect Password", "info")

            return redirect(url_for("user_settings"))
        return render_template("user_settings.html", form = form)
    else:
        return redirect(url_for("login"))

@app.route("/create_post/", methods=["GET", "POST"])
def create_post():
    if "user" in session:
        user_id = session["user_id"]
        user = get_user(id=user_id)
        form = PostForm()
        if request.method == "POST" and form.validate_on_submit():
            
            text = form.text.data
            media = form.media.data

            if text == "" and media == "":
                flash("Text and Media Fields cannot both be blank!")
                return redirect(url_for("create_post"))
            
            elif media == "":
                insert_post(user=user, text=text)
                flash("Post Created!")
                return redirect(url_for("home"))

            elif text == "":
                insert_post(user=user, text=text)
                filename = secure_filename(media.filename)
                media.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                media = Media(
                    file_path = media
                )

                flash("Post Created!")
                return redirect(url_for("home"))
            
            else:
                insert_post(user=user, text=text)
                filename = secure_filename(media.filename)
                media.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                media = Media(
                    file_path = media
                )
                flash("Post Created!")
                return redirect(url_for("home"))
            
        return render_template("create_post.html", form = form)
    
    else:
        return redirect(url_for("login"))


@app.route("/search/", methods=["GET", "POST"])
def search():
    form = SearchForm()
    if request.method == "POST" and form.validate_on_submit():
        user_data = form.user_query.data
        #text_data = form.text_query.data
        if user_data == "":
            flash("Fields cannot be blank!")
            return redirect(url_for("search"))
        
        elif exists_user(user_name=user_data):
            return redirect(url_for("user", dynamic_user = user_data))
        
    return render_template("search.html", form = form)

if __name__ == "__main__":
    app.run()
