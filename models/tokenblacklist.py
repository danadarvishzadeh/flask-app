
from datetime import datetime
from discussion.app import db

class TokenBlackList(db.Model):

    __tablename__ = 'token_black_list'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

    token = db.Column(db.String(500), unique=True, nullable=False)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.commit()
        return self