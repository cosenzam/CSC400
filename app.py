from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from forms import CreateAccountForm, LoginForm
import connect
import models

# pip install flask flask-wtf SQLAlchemy passlib flask-login

app = Flask(__name__)
app.secret_key = "asdf"
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{connect.MYSQL_USER}:{connect.MYSQL_PASS}@{connect.MYSQL_IP}/{connect.MYSQL_DB}'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days = 7) # session length

db = SQLAlchemy(app)

# Finds if user exists
def found_user(user):
    return bool(models.users.query.filter_by(username=user).first())

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
        username = form.username.data
        print(username)
        print(found_user(username))
        if not found_user(username):
            session["user"] = username # add user to session
            email = form.email.data
            password = form.password.data
            hashed_password = sha256_crypt.hash(password)
            user = models.users(username, email, hashed_password)
            db.session.add(user)
            db.session.commit()
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
            db.session.commit()
            flash("Email saved", "info")

        return render_template("user.html", username = user, email = email)
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    # Create all database tables in models.py
    models.create_tables()
    
    # Delete all database tables
    #models.delete_tables()

    app.run()