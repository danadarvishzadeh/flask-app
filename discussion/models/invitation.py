from datetime import datetime
from sqlalchemy import UniqueConstraint
from discussion.app import db

class Invitation(db.Model):

    __tablename__ = 'invitations'

    __table_args__ = (
        UniqueConstraint('owner_id', 'partner_id', name='unique_invitation'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=False)