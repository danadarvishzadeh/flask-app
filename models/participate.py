from datetime import datetime
from discussion.app import db


class Participate(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)
    
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    partner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))