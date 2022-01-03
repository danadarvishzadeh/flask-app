
from datetime import datetime
from sqlalchemy import UniqueConstraint, Index
from discussion.app import db

class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), primary_key=True)
    started_following = db.Column(db.DateTime, default=datetime.now())
