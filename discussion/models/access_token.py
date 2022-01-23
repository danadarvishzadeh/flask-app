from datetime import datetime

from sqlalchemy import Index

from discussion.app import db


class AccessToken(db.Model):
    
    __tablename__ = 'access_tokens'

    __table_args__ = (
        Index('access_owner_index', 'owner_id'),
        Index('access_token_index', 'token'),
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

    expires_in = db.Column(db.Interval)
    token = db.Column(db.String(32), unique=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    refresh_token = db.relationship('RefreshToken', backref='access_token', lazy='selectin', cascade='all, delete')

    @staticmethod
    def find(token):
        token = AccessToken.query.filter_by(token=token).first()
        if not token:
            raise ValueError
        return token

    @property
    def has_expired(self):
        return datetime.utcnow() > self.created_at + self.expires_in
    
    @property
    def is_invalid(self):
        return self.has_expired or not self.is_active
    
    @classmethod
    def depricate_tokens(cls, owner_id):
        delete_query = cls.__table__.delete().where(cls.owner_id == owner_id)
        db.session.execute(delete_query)
        db.session.commit()