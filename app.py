from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

from flask import Flask, json, make_response, jsonify
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import LOG_CONFIG, config
from flask_smorest import Api

dictConfig(LOG_CONFIG)




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

db = SQLAlchemy(model_class=BaseModel)
migrate = Migrate()
ma = Marshmallow()
api = Api()

def configure_blueprints(app):
    for blueprint in app.config['BLUEPRINTS']:
        bp = __import__('discussion.blueprints.%s' % blueprint, fromlist=[blueprint])
        api.register_blueprint(getattr(bp, 'bp'))

def register_error_handlers(app):
    def error(e):
        response = jsonify({
            "code": e.code,
            "status": e.name,
            "message": e.message,
            "errors": getattr(e, 'errors', None) or {}
        })
        response.status = e.code
        return response
    
    errors_file = __import__('discussion.utils.errors', fromlist=['errors'])
    for err in errors_file.__all__:
        app.register_error_handler(getattr(errors_file, err), error)


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    api.init_app(app)

    configure_blueprints(app)
    register_error_handlers(app)


    return app