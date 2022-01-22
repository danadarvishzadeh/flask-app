from datetime import datetime
from sqlalchemy import UniqueConstraint
from discussion.app import db
from discussion.models.participate import Participate
from sqlalchemy.dialects.postgresql import ENUM
from enum import Enum

class StatusEnum(Enum):
    sent = 'Sent'
    accepted = 'Accepted'
    rejected = 'Rejected'


status_enums = ENUM(StatusEnum, name='status', values_callable=lambda x: [str(x.value) for x in StatusEnum])


class Invitation(db.Model):

    __tablename__ = 'invitations'

    __table_args__ = (
        UniqueConstraint('owner_id', 'partner_id', 'discussion_id', name='unique_invitation'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

    body = db.Column(db.Text, nullable=False)
    # status = db.Column(db.String(10), default="Sent")
    status = db.Column(status_enums, server_default="Sent", nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=False)
    
    def update(self, response_data):
        if response_data.get('status') == 'Accepted':
            Participate(
                owner_id=self.owner_id,
                partner_id=self.partner_id,
                discussion_id=self.discussion_id
            ).save()
        super().update(response_data)