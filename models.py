from datetime import datetime, timedelta
from flask import url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
# from flask_login import UserMixin
from discussion.app import db
import jwt
from flask import current_app


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), primary_key=True)
    started_following = db.Column(db.DateTime, default=datetime.now())


class Participate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))
    date_started = db.Column(db.DateTime, default=datetime.now())


class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.now())
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    invited_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128))
    created_discussions = db.relationship('Discussion', backref='creator', lazy=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    invitations_sent = db.relationship('Invitation',
            backref='inviter',
            primaryjoin=id==Invitation.inviter_id)
    invitations_recived = db.relationship('Invitation',
            backref='invited',
            primaryjoin=id==Invitation.invited_id)
    host_for = db.relationship('Participate',
            backref='host',
            primaryjoin=id==Participate.host_id)
    participated_with_users = db.relationship('Participate',
            backref='participant',
            primaryjoin=id==Participate.participant_id)

    def encode_auth_token(self):
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=0, seconds=60),
                'iat': datetime.utcnow(),
                'sub': self.id
            }
            token = jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
            return token
        except Exception as e:
            return e
            pass

    @property
    def password(self):
        raise ValueError('not readable.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_check(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            user = User.query.get(payload['sub'])
            if user:
                return user
            else:
                raise Exception(jsonify({'error': 'Invalid token. Please log in again.'}))
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError(jsonify({'error': 'Signature expired. Please log in again.'}))
        except jwt.InvalidTokenError:
            raise jwt.ExpiredSignatureError(jsonify({'error': 'Invalid token. Please log in again.'}))

    

class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts = db.relationship('Post', backref='parent_discussion', lazy=True)
    
    followed_by = db.relationship('Follow', backref='discussion', lazy=True)
    participants = db.relationship('Participate', backref='discussion')
    invitations = db.relationship('Invitation', backref='discussion', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))


class TokenBlackList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False, default=datetime.now())