from datetime import datetime
from sqlalchemy import UniqueConstraint, Index
from discussion.app import db


class Participate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'))
    date_started = db.Column(db.DateTime, default=datetime.now())
