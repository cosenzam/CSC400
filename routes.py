from flask import Flask, redirect, url_for, render_template, session, flash, request
from flask_mail import Mail, Message
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import timedelta, datetime, time
from passlib.hash import sha256_crypt
from forms import CreateAccountForm, LoginForm, UserProfileForm, UserSettingsForm, PostForm, SearchForm, RecoveryForm, ResetPasswordForm
from connect import db_connect #connect.py method that handles all connections, returns engine.
from models import Base, User, Post, Interaction, Media, MediaCollection, Follows
from email_validator import validate_email, EmailNotValidError
import models
from models import (insert_user, get_user, exists_user, insert_interaction, insert_post, exists_post, get_post, follow, unfollow, upload_collection, 
    get_latest_replies, get_latest_post, get_latest_posts, get_interaction)
import os, os.path
from pathlib import Path
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired
from run import app
from functions import (validateEmail, validatePassword, getPostRecency, postDateFormat, get_token, send_recovery_email, send_signup_email, 
    get_reply_ajax_data, get_post_ajax_data, serial, mail, get_follow_ajax_data, to_date_and_time, get_home_ajax_data)
import json

#data base connections
engine = db_connect()
Session_MySQLdb = sessionmaker(engine)
db_session = Session_MySQLdb()

models.session = db_session

# Base.metadata.drop_all(engine, checkfirst=False)

# Create all database tables in models.pygi
Base.metadata.create_all(engine)

@app.route("/")
def home():
    if "user" in session:
        current_user = get_user(user_name = session["user"])
        posts = current_user.get_following_posts(current_user.get_following())
        if len(posts) > 0:
                last_post_id = posts[len(posts) - 1].id
        else:
            last_post_id = 1
        
        print(last_post_id)

        return render_template("index.html", current_user = current_user, posts = posts, get_user = get_user, getPostRecency = getPostRecency, postDateFormat = postDateFormat, 
        last_post_id = last_post_id, to_date_and_time = to_date_and_time)
    else:
        return render_template(url_for("login"))

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
        elif not validateEmail(email):
            return redirect(url_for("create_account"))
        elif not validatePassword(password, confirm_password):
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
            send_signup_email(email)

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
        user = exists_user(user_name=user_name)
        if user: 
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
        user_profile = get_user(user_name=session["user"])
        current_user = user_profile
        following_count = current_user.get_following_count()
        follower_count = current_user.get_follower_count()

        #a user object has a list of post objects made by that user
        #postings = user_profile.posts
        postings = get_latest_posts(user_profile, end=7)

        if len(postings) > 0:
            last_post_id = postings[len(postings) - 1].id
        else:
            last_post_id = 1
        #files = media.file_path

        if request.method == "POST" and form.validate_on_submit():
            
            text = form.text.data
            media = form.media.data

            #if get_latest_post(user).timestamp == datetime.now():
                #flash("Please wait before posting again", "info")
                #return redirect(url_for("user", dynamic_user = session["user"]))

            if media is not None:
                filename = secure_filename(media.filename)
                media.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            if media == "" and text == "":
                flash("Text and Media Fields cannot both be blank!")
                return redirect(url_for("create_post"))
            
            else:
                #insert_post() returns a post object

                post = insert_post(user_profile, text)
                #flash("Post Created!")
                
                return redirect(url_for("user", dynamic_user = session["user"]))

        return render_template("user.html", user_profile = user_profile, current_user = current_user, dynamic_user = dynamic_user, posts = postings, form = form,
        getPostRecency = getPostRecency, postDateFormat = postDateFormat, last_post_id = last_post_id, get_user = get_user, following_count = following_count,
        follower_count = follower_count, to_date_and_time = to_date_and_time)
    # If page is not the logged in user's
    else:
        user_profile = exists_user(user_name=dynamic_user)
        following_count = user_profile.get_following_count()
        follower_count = user_profile.get_follower_count()
        if user_profile:
            postings = get_latest_posts(user_profile, end=7)

            if len(postings) > 0:
                last_post_id = postings[len(postings) - 1].id
            else:
                last_post_id = 1
            if "user" in session:
                current_user = get_user(user_name=session["user"])

            return render_template("user.html", user_profile = user_profile, current_user = current_user, dynamic_user = dynamic_user, posts = postings, 
            getPostRecency = getPostRecency, postDateFormat = postDateFormat, is_following = current_user.is_following, last_post_id = last_post_id, 
            get_user = get_user, following_count = following_count, follower_count = follower_count, to_date_and_time = to_date_and_time)
        else:
            flash("User not found", "info")
            return redirect(url_for("home"))

@app.route("/edit_profile/", methods=["POST", "GET"])
def edit_profile():
    if "user" in session:
        user = session["user"]
        user_id = session["user_id"]
        form = UserProfileForm()

        user = get_user(id=user_id)

        if request.method == "GET":

            if user.bio != None:
                form.user_bio.data = user.bio
            if user.first_name != None:
                form.first_name.data = user.first_name
            if user.middle_name != None:
                form.middle_name.data = user.middle_name
            if user.last_name != None:
                form.last_name.data = user.last_name
            if user.pronouns != None:
                form.pronouns.data = user.pronouns
            if user.occupation != None:
                form.occupation.data = user.occupation
            if user.location != None:
                form.location.data = user.location
            if user.date_of_birth != None:
                form.date_of_birth.data = user.date_of_birth

            '''
            if profile.profile_picture_media_id != "NULL":
                form.profile_picture_media_id.data = profile.profile_picture_media_id
                filename = secure_filename(profile.profile_picture_media_id.filename)
                profile.profile_picture_media_id.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            '''

        if request.method == "POST" and form.validate_on_submit():

            #profile is a user object, User.update() take kwargs for each of its fields.
            user.update(
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
                elif validateEmail(email):
                    user.update(email = email)
                    flash("Email saved", "info")

            if current_password:
                if sha256_crypt.verify(current_password, user.password):
                    if sha256_crypt.verify(new_password, user.password):
                        flash("New password cannot be old password", "info")
                    elif new_password and validatePassword(new_password, confirm_password):
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
            
            else:
                #we should have a way to get a list of filenames in the upload screen
                #paths = []
                #for file in media.filenames:
                # filename = secure_filename(file)
                # paths.append(filename)
                # media.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                post = insert_post(user=user, text=text)

                if media != "":
                    file_paths = []

                    filename = secure_filename(media.filename)
                    path = Path(os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), str(post.id), filename))
                    file_paths.append(str(path))

                    #in loop should be path + filename
                    with open(path, "w") as file:
                        media.save(file)

                    upload_collection(user, post, file_paths)

                
                flash("Post Created!")
                return redirect(url_for("home"))
            
        return render_template("create_post.html", form = form)
    
    else:
        return redirect(url_for("login"))

@app.route("/post/<post_id>", methods=["GET", "POST"])
def view_post(post_id):
    form = PostForm()

    post = get_post(post_id)
    user = get_user(user_name = session["user"])
    if post != None:
        #print(post_id)
        replies = get_latest_replies(post_id = post.id)
        #replies.extend(get_replies_before_ajax(post_id = 45))
        #replies = post.get_replies()
        #print(replies)
        # last reply id for ajax to use python function
        if len(replies) > 0:
            last_reply_id = replies[len(replies) - 1].id
        else:
            last_reply_id = 1
        # load post from id
        if "user" in session:
            text = form.text.data
            media = form.media.data

            # breaks if user doesnt have any posts
            #if get_latest_post(user).timestamp == datetime.now():
                #flash("Please wait before posting again", "info")
                #return redirect(url_for("post", post_id = post.id))

            if request.method == "POST" and form.validate_on_submit:

                if text == "" and media == "":
                    flash("Text and Media Fields cannot both be blank!")
                    return redirect(url_for("view_post", post_id = post.id))
                else:
                    post.insert_reply(user, text)
                    return redirect(url_for("view_post", post_id = post.id))
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("home"))

    return render_template("view_post.html", post = post, replies = replies, getPostRecency = getPostRecency, postDateFormat = postDateFormat,
        get_user = get_user, form = form, last_reply_id = last_reply_id, to_date_and_time = to_date_and_time)

@app.route("/post/<post_id>/like")
def like(post_id):
    if "user" in session:

        from_user = get_user(user_name = session["user"])
        post = get_post(post_id)

        if not post.is_liked(from_user):
            post.like(from_user)
            return "like", 200
        else:
            post.unlike(from_user)
            return "unlike", 200

    else:
        flash("You must be logged in to like", "info")
        return redirect(url_for("login"))
        #return redirect(request.referrer)

@app.route("/recover_account", methods=["POST", "GET"])
def recover_account():
    form = RecoveryForm()
    if "user" not in session:
        if request.method == "POST" and form.validate_on_submit():
            email = form.email.data
            if get_user(email=email):
                user = get_user(email=email)
                user_name = user.user_name
                print(user_name)
                
                token = get_token(user)
                print(token)

                send_recovery_email(token, user.email)
                flash("Recovery email sent", "info")

                return redirect(url_for("login"))
            else:
                flash("Account not found", "info")
                return redirect(url_for("recover_account"))

        return render_template("recover_account.html", form = form)
    else:
        return redirect(url_for("home"))

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset(token):
    form = ResetPasswordForm()
    if "user" in session:
        return redirect(url_for('home'))
    try:
        # returns a dict
        user_id_dict = serial.loads(token, max_age=900)
    except:
        flash("Token has expired or is invalid", "info")
        return redirect(url_for("recover_account"))

    user = get_user(id=user_id_dict['user_id'])

    if request.method == "POST" and form.validate_on_submit():

        password = form.password.data
        confirm_password = form.confirm.data
        if validatePassword(password, confirm_password):
            hashed_password = sha256_crypt.hash(password)
            user.update(password = hashed_password)

        flash("Password Changed", "info")
        return redirect(url_for('login'))

    return render_template('reset_password.html', form = form)

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

@app.route("/user/<dynamic_user>/follow")
def follow_user(dynamic_user):
    if "user" in session:
        if session["user"] == dynamic_user:
            flash("You cannot follow yourself", "info")
            return redirect(url_for("user", dynamic_user = dynamic_user))
        else:
            from_user = get_user(user_name = session["user"])
            to_user = get_user(user_name = dynamic_user)
            if not from_user.is_following(to_user):
                follow(to_user, from_user)
                return "follow", 200
            else:
                unfollow(to_user, from_user)
                return "unfollow", 200
                #return redirect(url_for("user", dynamic_user = dynamic_user))
    else:
        flash("You must be logged in to follow", "info")
        return redirect(url_for("login"))

@app.route("/following")
def following_list():
    if "user" in session:
        current_user = get_user(user_name = session["user"])

        users = []
        following_list = current_user.get_following()
        
        if following_list:
            users = map(get_user, following_list)

        return render_template("following_list.html", current_user = current_user, users = users, following_list = following_list)

    else:
        return redirect(url_for("login"))

@app.route("/reply_scroll/<reply_id>")
def reply_scroll(reply_id):
    replies = get_reply_ajax_data(reply_id)
    return replies, 200

@app.route("/post_scroll/<post_id>")
def post_scroll(post_id):
    posts = get_post_ajax_data(post_id)
    return posts, 200

@app.route("/follow_scroll/<interaction_id>")
def follow_scroll(interaction_id):
    following = get_follow_ajax_data(get_interaction(interaction_id))
    return following, 200

@app.route("/home_scroll/<post_id>")
def home_scroll(post_id):
    posts = get_home_ajax_data(post_id)
    return posts, 200