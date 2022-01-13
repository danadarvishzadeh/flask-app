from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

import logging
from flask import Flask, json, make_response, jsonify
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import LOG_CONFIG, config
from flask_smorest import Api
from discussion.models import BaseModel

def configure_logger():
    dictConfig(LOG_CONFIG)

db = SQLAlchemy(model_class=BaseModel)
migrate = Migrate()
ma = Marshmallow()
api = Api()

def configure_blueprints(app):
    for blueprint in app.config['BLUEPRINTS']:
        bp = __import__('discussion.blueprints.%s' % blueprint, fromlist=[blueprint])
        api.register_blueprint(getattr(bp, 'bp'))

def configure_errorhandlers(app):
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


configure_logger()

def create_app(config_name='default'):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    api.init_app(app)

    configure_blueprints(app)
    configure_errorhandlers(app)

    request_logger = logging.getLogger('request_logger')
    response_logger = logging.getLogger('response_logger')
    @app.before_request
    def before_request_logging():
        request_logger.info('')

    @app.after_request
    def after_request_logging(response):
        response_logger.info('', extra={'response': response})
        return response

    return app