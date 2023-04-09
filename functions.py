from flask import Flask, url_for, session
from flask_mail import Mail, Message
from run import app
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired
import models
from models import get_replies_before, get_user, get_user_posts_before
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
    replies = get_replies_before(post_id)
    l = []
    for reply in replies:
        user = get_user(id = reply.user_id)
        from_user = get_user(user_name = session["user"])
        l.append(
            {"post_id": reply.id,
            "user_name": user.user_name,
            "timestamp": reply.timestamp.strftime("%x") + " " + reply.timestamp.strftime("%X"),
            "recency": postDateFormat(reply, getPostRecency(reply)),
            "text": reply.text,
            "is_liked": reply.is_liked(from_user)})
    return l

def get_post_ajax_data(post_id):
    from_user = get_user(user_name = session["user"])
    posts = get_user_posts_before(from_user, post_id)
    l = []
    for post in posts:
        user = get_user(id = post.user_id)
        l.append(
            {"post_id": post.id,
            "user_name": user.user_name,
            "timestamp": post.timestamp.strftime("%x") + " " + post.timestamp.strftime("%X"),
            "recency": postDateFormat(post, getPostRecency(post)),
            "text": post.text,
            "is_liked": post.is_liked(from_user)})
    return l
