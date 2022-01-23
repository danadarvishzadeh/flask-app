from datetime import datetime

from sqlalchemy import Index

from discussion.app import db


class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'

    __table_args__ = (
        Index('refresh_owner_index', 'owner_id'),
        Index('refresh_token_index', 'token'),
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

    expires_in = db.Column(db.Interval)
    token = db.Column(db.String(32), unique=True)
    
    access_token_id = db.Column(db.Integer, db.ForeignKey('access_tokens.id', ondelete="CASCADE"))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def find(token):
        token = RefreshToken.query.filter_by(token=token).first()
        if not token:
            raise ValueError
        return token

    @property
    def is_invalid(self):
        return datetime.utcnow() > self.expires_in + self.created_at or not self.is_active
        
    @classmethod
    def depricate_tokens(cls, owner_id):
        delete_query = cls.__table__.delete().where(cls.owner_id == owner_id)
        db.session.execute(delete_query)
        db.session.commit()