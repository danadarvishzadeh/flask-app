from datetime import datetime

from sqlalchemy import Index, UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from discussion.app import db
from discussion.models.discussion import Discussion
from discussion.models.invitation import Invitation
from discussion.models.participate import Participate
from discussion.models.post import Post
from discussion.models.follow import Follow


class User(db.Model):

    __tablebame__ = 'users'

    __table_args__ = (
        Index('name_index', 'lastname', 'name'),
        UniqueConstraint('name', 'lastname', name='unique_person')
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    
    name = db.Column(db.String(64), nullable=False)
    lastname = db.Column(db.String(64), nullable=False)
    
    password_hash = db.Column(db.String(128))
    
    owned_discussions = db.relationship('Discussion', backref='owner', lazy=True)
    owned_posts = db.relationship('Post', backref='owner', lazy=True)
    owned_follows = db.relationship('Follow',
            backref='owner',
            primaryjoin=id==Follow.owner_id)

    owned_invitations = db.relationship('Invitation',
            backref='owner',
            primaryjoin=id==Invitation.owner_id)
    partnered_invitations = db.relationship('Invitation',
            backref='partner',
            primaryjoin=id==Invitation.partner_id)
    owned_participations = db.relationship('Participate',
            backref='owner',
            primaryjoin=id==Participate.owner_id)
    partnered_participations = db.relationship('Participate',
            backref='partner',
            primaryjoin=id==Participate.partner_id)
    
    @property
    def password(self):
        raise AttributeError()

    def password_check(self, password):
        return check_password_hash(self.password_hash, password)
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    @property
    def invited_users(self):
        return [i.partner for i in self.owned_invitations]
    
    @property
    def inviter_users(self):
        return [i.owner for i in self.partnered_invitations]
    
    @property
    def participated_users(self):
        return [i.partner for i in self.owned_participations]
    
    @property
    def partnered_users(self):
        return [i.owner for i in self.partnered_participations]
    
    @property
    def followed_discussions(self):
        return [i.owner for i in self.owned_follows]
    
    @property
    def participated_discussions(self):
        return [i.discussion for i in self.partnered_participations]
    
    @property
    def hosted_discussions(self):
        return [i.discussion for i in self.owned_participations]