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
def found_user(found_user):
    result = bool(db_session.query(models.User)
        .filter_by(user_name = found_user).first())
    return result

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view")
def view():
    return render_template("view.html", values=models.users.query.all())

@app.route("/create_account/", methods=["POST", "GET"])
def create_account():
    form = CreateAccountForm()
    if request.method == "POST" and form.validate_on_submit():
        session.permanent = True
        user_name = form.username.data
        print(user_name)
        print(found_user(user_name))
        if not found_user(user_name):
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
            flash("Username already exists", "info")
            return redirect(url_for("create_account"))
    else:
        if "user" in session:
            flash("Already logged in", "info")
            return redirect(url_for("user"))
    return render_template("create_account.html", form = form)
    
    

@app.route("/login/", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        print(username)
        print(password)
        if found_user(username):
            user_query = models.users.query.filter_by(username=username).first()
            hashed_password = user_query.password
            if sha256_crypt.verify(password, hashed_password):
                session.permanent = True
                session["user"] = username
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

    # Change user email, change later, placeholder for now
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = models.users.query.filter_by(username=user).first()
            found_user.email = email
            db_session.commit()
            flash("Email saved", "info")

        return render_template("user.html", username = user, email = email)
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":

    
    # Delete all database tables
    #models.delete_tables()

    app.run()