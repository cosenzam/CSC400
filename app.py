from flask import Flask, redirect, url_for, render_template, request, session, flash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import timedelta
from passlib.hash import sha256_crypt
from forms import CreateAccountForm, LoginForm, UserProfileForm, UserSettingsForm, PostForm
from connect import db_connect #connect.py method that handles all connections, returns engine.
from models import Base, User, UserProfile, Post
from email_validator import validate_email, EmailNotValidError

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

    exists = db_session.query(User.id).filter_by(user_name=user_name).first() is not None
    return exists

# Finds if email exists
#def found_email(email):

    #exists = db_session.query(User.id).filter_by(email=email).first() is not None   
    #return exists

# Find if email exists in DB and is a valid format
def valid_email(email):

    exists = db_session.query(User.id).filter_by(email=email).first() is not None 
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
        if found_user(user_name):
            flash("Username already exists", "info")
            return redirect(url_for("create_account"))
        elif not valid_email(email):
            return redirect(url_for("create_account"))
        elif not valid_pass(password, confirm_password):
            return redirect(url_for("create_account"))
        else: 
            session["user"] = user_name # add user to session
            hashed_password = sha256_crypt.hash(password)
            user = User(
                user_name = user_name, 
                email = email, 
                password = hashed_password
                )

            db_session.add(user)
            db_session.commit()
            #gonna add current user's user_id to session
            session["user_id"] = int(user.id)
            #creating entry in user profile to fill later
            user_profile = UserProfile(
                user_id = user.id
            )
            
            db_session.add(user_profile)
            db_session.commit()

            user.profile_id = user_profile.id
            db_session.commit()

            return redirect(url_for("user", dynamic_user = session["user"]))
    else:
        if "user" in session:
            flash("Already logged in", "info")
            return redirect(url_for("user", dynamic_user = session["user"]))
    return render_template("create_account.html", form = form)
    
    

@app.route("/login/", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        #print(user_name)
        #print(password)
        if found_user(user_name):

            user_query = select(User).where(User.user_name == user_name)
            user = db_session.scalars(user_query).one()
            hashed_password = user.password
            if sha256_crypt.verify(password, hashed_password):
                session.permanent = True
                session["user"] = user_name
                session["user_id"] = user.id
                flash("Login Success", "info")
                return redirect(url_for("user", dynamic_user = session["user"]))
            else:
                flash("Incorrect Password", "info")
                return redirect(url_for("login"))
        else:
            flash("User not found", "info")
            return redirect(url_for("login"))
    else:
        if "user" in session:
            flash("Already Logged in", "info")
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
        user_id = session["user_id"]
        user_profile_query = select(UserProfile).where(UserProfile.id == user_id)
        profile = db_session.scalars(user_profile_query).one()

        postings = db_session.query(Post).filter_by(user_id=user_id).order_by(Post.date_posted.desc()).all()

        return render_template("user.html", profile = profile, dynamic_user = dynamic_user, posts = postings)
    # If page is not the logged in user's
    else:
        if found_user(dynamic_user):
            user_id = select(User.id).where(User.user_name == dynamic_user)
            user_profile_query = select(UserProfile).where(UserProfile.id == user_id)
            profile = db_session.scalars(user_profile_query).one()

            postings = db_session.query(Post).filter_by(user_id=user_id).order_by(Post.date_posted.desc()).all()

            return render_template("user.html", profile = profile, dynamic_user = dynamic_user, posts = postings)
        else:
            flash("User not found", "info")
            return redirect(url_for("home"))

@app.route("/edit_profile/", methods=["POST", "GET"])
def edit_profile():
    if "user" in session:
        user = session["user"]
        user_id = session["user_id"]
        form = UserProfileForm()

        if request.method == "POST" and form.validate_on_submit():
            user_profile_query = select(UserProfile).where(UserProfile.user_id == user_id)
            user_profile = db_session.scalars(user_profile_query).one()

            if form.user_bio.data:
                user_profile.bio = form.user_bio.data
            if form.first_name.data:
                user_profile.first_name = form.first_name.data
            if form.middle_name.data:
                user_profile.middle_name = form.middle_name.data
            if form.last_name.data:
                user_profile.last_name = form.last_name.data
            if form.gender.data:
                user_profile.gender = form.gender.data
            if form.pronouns.data:
                user_profile.pronouns = form.pronouns.data
            if form.address.data:
                user_profile.address = form.address.data
            if form.occupation.data:
                user_profile.occupation = form.occupation.data
            if form.city.data:
                user_profile.city = form.city.data
            if form.country.data:
                user_profile.country = form.country.data
            if form.zip.data:
                user_profile.zip = form.zip.data
            if form.date_of_birth.data:
                user_profile.date_of_birth = form.date_of_birth.data

            db_session.commit()
            flash("Your profile has been updated", "info")
            return redirect(url_for("edit_profile"))

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
            user_query = db_session.query(User).filter_by(user_name=user).first()
            confirm_password = form.confirm.data
            if form.email.data and valid_email(form.email.data):
                user_query.email = form.email.data
                db_session.commit()
                flash("Email saved", "info")
            if form.password.data and valid_pass(form.password.data, confirm_password):
                hashed_password = sha256_crypt.hash(form.password.data)
                user_query.password = hashed_password
                db_session.commit()
                flash("Password sucessfully changed", "info")
            return redirect(url_for("user_settings"))
        return render_template("user_settings.html", form = form)
    else:
        return redirect(url_for("login"))
    
@app.route("/create_post/", methods=["POST", "GET"])
def create_post():
    if "user" in session:
        user_id = session["user_id"]
        form = PostForm()
        if request.method == "POST" and form.validate_on_submit():
            
            text = form.text.data
            media = form.media.data

            if media == "" and text == "":
                flash("Text and Media Fields cannot both be blank!")
                return redirect(url_for("create_post"))
            
            else:
                post = Post(
                    text = text,
                    media = media,
                    user_id = user_id
                )

                db_session.add(post)
                db_session.commit()
                flash("Post Created!")
                #print(post)
                return redirect(url_for("home"))
        return render_template("create_post.html", form = form)
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()
