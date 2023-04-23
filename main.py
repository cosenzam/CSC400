from flask import Flask, request, abort
import logging
import os
from datetime import timedelta, datetime, time

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = "asdf"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'cosenzam.test@gmail.com'
app.config['MAIL_PASSWORD'] = 'vsfomiiiayzgusks'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.permanent_session_lifetime = timedelta(days = 7) # session length
app.config['UPLOAD_FOLDER'] = 'static/images/'

from routes import *


if __name__ == "__main__":
    logging.info(os.getcwd())
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
