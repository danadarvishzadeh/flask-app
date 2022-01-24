from datetime import datetime
from email.policy import default

from sqlalchemy import Index, UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash
from flask import g
from discussion.app import db
from discussion.models.discussion import Discussion
from discussion.models.invitation import Invitation
from discussion.models.participate import Participate
from discussion.models.follow import Follow


class User(db.Model):

    __tablename__ = 'users'

    __table_args__ = (
        Index('name_index', 'last_name', 'first_name'),
        UniqueConstraint('first_name', 'last_name', name='unique_person')
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    last_login = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    
    password_hash = db.Column(db.String(128))
    last_token = db.Column(db.String(32), default='')
    
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
        if password:
            return check_password_hash(self.password_hash, password)
        else:
            return False
    
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
        
    def follow(self, discussion_id):
        discussion = Discussion.query.get(discussion_id)
        follow = Follow()
        follow.partner_id = g.user.id
        follow.discussion_id = discussion_id
        follow.save()

    def unfollow(self, discussion_id):
        follow = Follow.query.filter_by(discussion_id=discussion_id).first()
        follow.delete()
    
    def update_last_seen(self):
        self.update({'last_seen': datetime.utcnow()})
    
    def update_last_login(self):
        self.update({'last_login': datetime.utcnow()})