from datetime import datetime, timedelta

from flask import current_app, jsonify, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import UniqueConstraint, Index
from discussion.app import db


class TokenBlackList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False, default=datetime.now())


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
    __table_args__ = (
        UniqueConstraint('inviter_id', 'invited_id', name='unique_invitation'),
    )
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.now())
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    invited_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)


class User(db.Model):
    __table_args__ = (
        Index('name_index', 'lastname', 'name'),
    )
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

    @property
    def password(self):
        raise ValueError('not readable.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_check(self, password):
        return check_password_hash(self.password_hash, password)


class Discussion(db.Model):

    __table_args__ = (
        UniqueConstraint('title', 'creator_id', name='unique_discussion'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts = db.relationship('Post', backref='parent_discussion', lazy=True)
    
    followed_by = db.relationship('Follow', backref='discussion', lazy=True)
    participants = db.relationship('Participate', backref='discussion')
    invitations = db.relationship('Invitation', backref='discussion', lazy=True)

    def get_participants(self):
        return [p.participant for p in self.participants]

    def get_participant_ids(self):
        return [p.participant_id for p in self.participants]
    
    def get_follower_ids(self):
        return [f.follower_id for f in self.followed_by]


class Post(db.Model):
    __table_args__ = (
        UniqueConstraint('author_id', 'discussion_id', 'body', name='creator_unique_post'),
        Index('author_discussion', 'author_id', 'discussion_id'),
    )
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))
