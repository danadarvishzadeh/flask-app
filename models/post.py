from datetime import datetime
from sqlalchemy import UniqueConstraint, Index
from discussion.app import db

class Post(db.Model):

    __tablename__ = 'posts'

    __table_args__ = (
        UniqueConstraint('owner_id', 'discussion_id', 'body', name='creator_unique_post'),
        Index('author_discussion', 'owner_id', 'discussion_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

    body = db.Column(db.Text, nullable=False)
    
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self