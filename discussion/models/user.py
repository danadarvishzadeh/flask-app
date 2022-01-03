from datetime import datetime

from sqlalchemy import Index, UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from discussion.app import db


class User(db.Model):
    __table_args__ = (
        Index('name_index', 'lastname', 'name'),
        UniqueConstraint('name', 'lastname', name='unique_person')
    )
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    
    name = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    
    password = db.Column(db.String(128))
    
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

    @password.setter
    def password(self, password):
        self.password = generate_password_hash(password)

    def password_check(self, password):
        return check_password_hash(self.password, password)
