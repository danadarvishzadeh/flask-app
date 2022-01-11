__all__ = [
    'Discussion',
    'User',
    'Post',
    'Invitation',
    'Participate',
    'Follow'
]



from flask_sqlalchemy import Model


class BaseModel(Model):

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def update(self, data):
        self.query.update(dict())
        db.session.commit()
    
    def delete(self):
        db.session.delete()