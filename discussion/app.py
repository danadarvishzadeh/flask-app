from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

from flask import Flask, json, make_response
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import LOG_CONFIG, config

dictConfig(LOG_CONFIG)

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()


def configure_blueprints(app):
    for blueprint in app.config['BLUEPRINTS']:
        bp = __import__('discussion.blueprints.%s' % blueprint, fromlist=[blueprint])
        app.register_blueprint(getattr(bp, 'bp'))

def register_error_handlers(app):
    def error(e):
        response = make_response()
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.message,
        })
        response.content_type = "application/json"
        response.status = e.code
        return response
    
    errors_file = __import__('discussion.errors', fromlist=['errors'])
    for err in errors_file.__all__:
        app.register_error_handler(getattr(errors_file, err), error)


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    configure_blueprints(app)
    register_error_handlers(app)

    return app

# if __name__ == "__main__":
#     create_app().run(debug=True)