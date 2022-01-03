from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import config, LOG_CONFIG
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig


dictConfig(LOG_CONFIG)

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()


def configure_blueprints(app):
    for blueprint in app.config['BLUEPRINTS']:
        bp = __import__('discussion.blueprints.%s' % blueprint, fromlist=[blueprint])
        app.register_blueprint(getattr(bp, 'bp'))


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    from discussion.models import Discussion, Post, User, Invitation, Participate, Follow
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    configure_blueprints(app)

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
