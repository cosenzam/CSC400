from flask import Flask, url_for, session, flash
from flask_mail import Mail, Message
from run import app
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired
import models
from models import get_replies_before, get_user, get_user_posts_before, get_post, exists_user, get_following_before, get_interaction
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta
import json

serial = Serializer(app.config['SECRET_KEY'])
mail = Mail(app)

# Find if email exists in DB and is a valid format
def validateEmail(email):

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
def validatePassword(password, confirm_password):
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
# recency_tuple = (seconds, mins, hours, days)
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

# timestamp conversion for post tooltips
def to_date_and_time(d):
    date = d.strftime("%x")
    time = d.strftime("%r")

    if time[0] == '0':
        time = time[1:]
        time = time[:4] + time[7:]
    else:
        time = time[:5] + time[8:]

    return date + " " + time

def get_token(user):
    token = serial.dumps({'user_id': user.id})
    return token

def send_recovery_email(token, email):
    msg = Message("Account Recovery", sender=app.config['MAIL_USERNAME'],
                        recipients=[email])
    link = url_for('reset', token=token, _external=True)
    msg.body = "Your account recovery link: "+link
    mail.send(msg)
    return print("Recovery email sent")

def send_signup_email(email):
    msg = Message("Thank you for signing up!", sender=app.config['MAIL_USERNAME'],
                        recipients=[email])
    link = url_for('login',  _external=True)
    msg.body = "Welcome! Log in here: "+link
    mail.send(msg)
    return print("Sign up email sent")

# give ajax the list of dictionary values it needs
def get_reply_ajax_data(post_id):
    from_user = get_user(user_name = session["user"])
    replies = get_replies_before(post_id)
    l = []
    for reply in replies:
        user = get_user(id = reply.user_id)
        l.append({
            "post_id": reply.id,
            "user_name": user.user_name,
            "timestamp": to_date_and_time(reply.timestamp),
            "recency": postDateFormat(reply, getPostRecency(reply)),
            "text": reply.text,
            "is_liked": reply.is_liked(from_user),
            "like_count": reply.like_count,
            "reply_count": reply.reply_count
            })
    return l

def get_post_ajax_data(post_id):
    from_user = get_user(user_name = session["user"])
    # get user id
    user = get_user(id = get_post(post_id).user_id)
    posts = get_user_posts_before(user, post_id)
    l = []
    for post in posts:
        l.append({
            "post_id": post.id,
            "user_name": user.user_name,
            "timestamp": to_date_and_time(post.timestamp),
            "recency": postDateFormat(post, getPostRecency(post)),
            "text": post.text,
            "is_liked": post.is_liked(from_user),
            "like_count": post.like_count,
            "reply_count": post.reply_count
            })
    return l

def get_follow_ajax_data(interaction):
    user_id = get_user(user_name = session["user"]).id
    print(interaction.id)
    follows = get_following_before(user_id, interaction)
    l = []
    for follow in follows:
        l.append({
            "user_name": get_user(user_id = follow.follows_user_id).user_name
        })
    return l

def get_timeline_data(post_id, followed_users):
    current_user = get_user(user_name = session["user"])
    