from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy


#ORM
db = SQLAlchemy()
from discussion.models import BaseModel
db.Model = db.make_declarative_base(BaseModel)
#Migration Extention
migrate = Migrate()


#Schema extention
marshmallow = Marshmallow()


#Auto document extention
api = Api()