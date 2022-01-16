
from datetime import datetime
from sqlalchemy import UniqueConstraint, Index
from discussion.app import db

class Follow(db.Model):

    __tablename__ = 'follows'
    __table_args__ = (
        UniqueConstraint('discussion_id', 'owner_id', name='unique_follow'),
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)


    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))