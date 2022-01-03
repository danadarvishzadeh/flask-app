from datetime import datetime

from sqlalchemy import Index, UniqueConstraint

from discussion.app import db
from discussion.models.post import Post


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
