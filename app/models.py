from time import time
from datetime import datetime
from flask_login import UserMixin
from flask_mail import Message

from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, app, mail

import jwt

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class CocktailDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=False)
    ingredients = db.Column(db.Text(), nullable=False)
    preparation = db.Column(db.Text(), nullable=False)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='author', lazy='dynamic')

    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')

    last_message_read_time = db.Column(db.DateTime, index=True, unique=True)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')


    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)



class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '< Message {}>'.format(self.body)


class CocktailDTO(object):

    def __init__(self, cocktail):
        self.name = "".join(cocktail.name.split('_')[1:]) if cocktail.name.split('_')[0].isnumeric() else cocktail.name
        self.ingredients = zip(cocktail.ingredients, cocktail.ingredient_quantity_unit)
        self.preparation = cocktail.preparation