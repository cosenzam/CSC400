from app import db

# Database Tables
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("username", db.String(64))
    email = db.Column("email", db.String(64))
    password = db.Column("password", db.String(144))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


def create_tables():
    db.create_all()

def delete_tables():
    db.drop_all()