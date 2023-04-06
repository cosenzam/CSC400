from flask import Flask
from flask_mail import Mail, Message
from run import app
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired

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