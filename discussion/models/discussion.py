from datetime import datetime

from sqlalchemy import Index, UniqueConstraint

from discussion.app import db
from discussion.models.post import Post
from discussion.models.follow import Follow
from discussion.models.participate import Participate
from discussion.models.invitation import Invitation

class Discussion(db.Model):

    __tablename__ = 'discussions'

    __table_args__ = (
        UniqueConstraint('title', 'owner_id', name='unique_discussion'),
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

    title = db.Column(db.String(64), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    posts = db.relationship('Post', backref='parent_discussion', lazy=True)
    
    followed_by = db.relationship('Follow', backref='discussion', lazy=True)
    partners = db.relationship('Participate', backref='discussion')
    invitations = db.relationship('Invitation', backref='discussion', lazy=True)

    @property
    def followers(self):
        return [i.owner for i in self.followed_by]

    @property
    def partner_users(self):
        return [i.partner for i in self.participants]
    
    @property
    def invited_users(self):
        return [i.partner for i in self.invitations]