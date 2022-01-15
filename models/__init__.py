__all__ = [
    'Discussion',
    'User',
    'Post',
    'Invitation',
    'Participate',
    'Follow'
]



from flask_sqlalchemy import Model
from discussion.extentions import db


class BaseModel(Model):

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def update(self, data):
        self.query.update(data)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()