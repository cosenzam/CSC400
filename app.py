from flask import Flask, redirect, url_for, render_template, request, session, flash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, case, literal_column
from datetime import timedelta
from passlib.hash import sha256_crypt
from forms import CreateAccountForm, LoginForm
from connect import db_connect #connect.py method that handles all connections, returns engine.
import models
from models import Base

#app settings
app = Flask(__name__)
app.secret_key = "asdf"
app.permanent_session_lifetime = timedelta(days = 7) # session length

#data base connections
engine = db_connect()
Session_MySQLdb = sessionmaker(engine)
db_session = Session_MySQLdb()

# Base.metadata.drop_all(engine, checkfirst=False)

# Create all database tables in models.pygi
Base.metadata.create_all(engine)

# Finds if user exists
def found_user(user_name):
    result = bool(db_session.query(models.User)
        .filter_by(user_name = user_name).first())
    return result

# Finds if email exists
def found_email(email):
    result = bool(db_session.query(models.User)
        .filter_by(email = email).first())
    return result

# Verifies password requirements | must contain at least 1 number and 1 letter
def valid_pass(password):
    has_letters = any(c.isalpha() for c in password)
    has_numbers = any(i.isdigit() for i in password)
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
    return render_template("view.html", values = db_session.query(models.User).all())

@app.route("/create_account/", methods=["POST", "GET"])
def create_account():
    form = CreateAccountForm()
    if request.method == "POST" and form.validate_on_submit():
        session.permanent = True
        user_name = form.user_name.data
        email = form.email.data
        password = form.password.data
        if found_user(user_name):
            flash("Username already exists", "info")
            return redirect(url_for("create_account"))
        elif found_email(email):
            flash("Email already in use", "info")
            return redirect(url_for("create_account"))
        elif not valid_pass(password):
            return redirect(url_for("create_account"))
        else: 
            session["user"] = user_name # add user to session
            email = form.email.data
            password = form.password.data
            hashed_password = sha256_crypt.hash(password)
            user = models.User(
                user_name = user_name, 
                email = email, 
                password = hashed_password
                )

            db_session.add(user)
            db_session.commit()

            #gonna add current user's user_id to session
            session["user_id"] = int(user.user_id)
            #creating entry in user profile to fill later
            user_profile = models.UserProfile(
                user_id = user.user_id
            )

            db_session.add(user_profile)
            db_session.commit()
            return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in", "info")
            return redirect(url_for("user"))
    return render_template("create_account.html", form = form)
    
    

@app.route("/login/", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        print(user+name)
        print(password)
        if found_user(user_name):
            user_query = models.users.query.filter_by(user_name=user_name).first()
            hashed_password = user_query.password
            if sha256_crypt.verify(password, hashed_password):
                session.permanent = True
                session["user"] = user_name
                flash("Login Success", "info")
                return redirect(url_for("user"))
            else:
                flash("Incorrect Password", "info")
                return redirect(url_for("login"))
        else:
            flash("User not found", "info")
            return redirect(url_for("login"))
    else:
        if "user" in session:
            flash("Already Logged in", "info")
            return redirect(url_for("user"))
    return render_template("login.html", form = form)

@app.route("/logout/")
def logout():
    if "user" in session:
        user = session["user"]
        session.pop("user", None)
        flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/user/", methods=["POST", "GET"])
def user():

    if "user" in session:
        user_bio = "This is the bio section"

        return render_template("user.html", user_name = user, user_bio = user_bio)
    else:
        return redirect(url_for("login"))

@app.route("/edit_profile/", methods=["POST", "GET"])
def edit_profile():
    if "user" in session:
        user = session["user"]
        form = UserProfileForm()

        if request.method == "POST" and form.validate_on_submit():
            user_bio = form.user_bio.data
            user_query = db_session.query(models.UserProfile).filter_by(user_name = user).first()
            user_query.user_profile.bio = user_bio
            db_session.commit()
            flash("Your bio has been updated", "info")
            print(user_bio)
            return redirect(url_for("user"))

        return render_template("edit_profile.html", user_name = user, form = form)
    else:
        flash("You must be logged in to edit your profile", "info")
        return redirect(url_for("login"))

@app.route("/settings/", methods=["POST","GET"])
def user_settings():
    if "user" in session:
        user = session["user"]
        form = UserSettingsForm()
        if request.method == "POST" and form.validate_on_submit():
            user_query = db_session.query(models.User).filter_by(user_name=user).first()
            email = form.email.data
            password = form.password.data
            if email != '' : # and valid email
                user_query.email = email
                db_session.commit()
                flash("Email saved", "info")
            if password != '' and valid_pass(password):
                hashed_password = sha256_crypt.hash(password)
                user_query.password = hashed_password
                db_session.commit()
                flash("Password sucessfully changed", "info")
            return redirect(url_for("user_settings"))
        return render_template("user_settings.html", form = form)
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()