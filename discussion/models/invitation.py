from datetime import datetime
from sqlalchemy import UniqueConstraint
from discussion.app import db

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
