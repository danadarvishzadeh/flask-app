from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import config, LOG_CONFIG
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
# from importlib import __import__


dictConfig(LOG_CONFIG)

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

# from discussion.blueprints.api.views import bp as api
# from discussion.blueprints.auth import bp as auth


def configure_blueprints(app):
    for blueprint in app.config['BLUEPRINTS']:
        bp = __import__('discussion.%s' % blueprint, fromlist=[blueprint])

        for route in bp.__all__:
            app.register_blueprint(getattr(bp, route))


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    from discussion.models import Discussion, Post, User, Invitation, Participate, Follow
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    configure_blueprints(app)
    # app.register_blueprint(auth)
    # app.register_blueprint(api)

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
