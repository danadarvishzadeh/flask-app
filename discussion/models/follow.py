
from datetime import datetime
from sqlalchemy import UniqueConstraint, Index
from discussion.app import db

class Follow(db.Model):

    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)


    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), primary_key=True)