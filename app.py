from flask import Flask, redirect, url_for, render_template, request, session, flash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import timedelta
from passlib.hash import sha256_crypt
from forms import CreateAccountForm, LoginForm, UserProfileForm, UserSettingsForm, PostForm
from connect import db_connect #connect.py method that handles all connections, returns engine.
import models
from models import Base, User, Post, Media, MediaCollection, Interaction, FollowLookup, \
    insert_user, get_user, insert_post
from email_validator import validate_email, EmailNotValidError

#app settings
app = Flask(__name__)
app.secret_key = "asdf"
app.permanent_session_lifetime = timedelta(days = 7) # session length

#data base connections
engine = db_connect()
Session_MySQLdb = sessionmaker(engine)
db_session = Session_MySQLdb()

# Base.metadata.drop_all(engine)

# Create all database tables in models.pygi
Base.metadata.create_all(engine)

models.session = db_session

# Find if email exists in DB and is a valid format
def valid_email(email):

    user = get_user(email=email)
    if user is not None:
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
        if get_user(user_name=user_name) is not None:
            flash("Username already exists", "info")
            return redirect(url_for("create_account"))
        elif not valid_email(email):
            return redirect(url_for("create_account"))
        elif not valid_pass(password, confirm_password):
            return redirect(url_for("create_account"))
        else: 
            session["user"] = user_name # add user to session
            hashed_password = sha256_crypt.hash(password)
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

        user = get_user(user_name=user_name)
        if user is not None:
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
        user = get_user(id=user_id)
        postings = user.posts

        if request.method == "POST" and form.validate_on_submit():
            
            text = form.text.data
            media = form.media.data

            if media == "" and text == "":
                flash("Text and Media Fields cannot both be blank!")
                return redirect(url_for("create_post"))
            
            else:
                post = insert_post(user, text)
                flash("Post Created!")
                #print(post)
                return redirect(url_for("user", dynamic_user = session["user"]), user=user)

    # If page is not the logged in user's
    else:
        user = get_user(user_name = dynamic_user)
        if  user is not None:

            postings = user.posts

            return render_template("user.html", dynamic_user = dynamic_user, posts = postings, user=user)
        else:
            flash("User not found", "info")
            return redirect(url_for("home"))

@app.route("/edit_profile/", methods=["POST", "GET"])
def edit_profile():
    if "user" in session:
        user = session["user"]
        user_id = session["user_id"]
        form = UserProfileForm()

        user = get_user(id = user_id)

        if request.method == "GET":
            if user.bio != "NULL":
                form.user_bio.data = user.bio
            if user.first_name != "NULL":
                form.first_name.data = user.first_name
            if user.middle_name != "NULL":
                form.middle_name.data = user.middle_name
            if user.last_name != "NULL":
                form.last_name.data = user.last_name
            if user.pronouns != "NULL":
                form.pronouns.data = user.pronouns
            if user.occupation != "NULL":
                form.occupation.data = user.occupation
            if user.location != "NULL":
                form.location.data = user.location
            if user.date_of_birth != "NULL":
                form.date_of_birth.data = user.date_of_birth

        if request.method == "POST" and form.validate_on_submit():

            user.update(
                bio = form.user_bio.data,
                first_name = form.first_name.data,
                middle_name = form.middle_name.data,
                last_name = form.last_name.data,
                pronouns = form.pronouns.data,
                occupation = form.occupation.data,
                location = form.location.data,
                date_of_birth = form.date_of_birth.data
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
        user = get_user(user_name = user_name)
        form = UserSettingsForm()
        if request.method == "POST" and form.validate_on_submit():
            confirm_password = form.confirm.data
            if form.email.data and valid_email(form.email.data):
                user.update(email=form.email.data)
                flash("Email saved", "info")
            if form.password.data and valid_pass(form.password.data, confirm_password):
                hashed_password = sha256_crypt.hash(form.password.data)
                user.update(password=hashed_password)
                flash("Password sucessfully changed", "info")
            return redirect(url_for("user_settings"))
        return render_template("user_settings.html", form = form)
    else:
        return redirect(url_for("login"))
    
@app.route("/create_post/", methods=["POST", "GET"])
def create_post():
    if "user" in session:
        user_id = session["user_id"]
        user = get_user(id=user_id)
        form = PostForm()
        if request.method == "POST" and form.validate_on_submit():
            
            text = form.text.data
            media = form.media.data

            if media == "" and text == "":
                flash("Text and Media Fields cannot both be blank!")
                return redirect(url_for("create_post"))
            
            else:
                post = insert_post(user, text)
                flash("Post Created!")
                return redirect(url_for("home"))
        return render_template("create_post.html", form = form)
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()
