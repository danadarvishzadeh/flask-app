import logging
from logging.config import dictConfig

from flask import Flask, jsonify

from discussion.extentions import api, db, marshmallow, migrate

from .config import config

logger = logging.getLogger(__name__)

def configure_logging(app):
    
    #Loading general logging configurations
    dictConfig(app.config.get('LOG_CONFIG'))

    request_logger = logging.getLogger('request_logger')
    response_logger = logging.getLogger('response_logger')

    #Registering before request logger
    @app.before_request
    def before_request_logging():
        request_logger.info('')

    #Registering after request logger
    @app.after_request
    def after_request_logging(response):
        response_logger.info('', extra={'response': response})
        return response


def configure_blueprints(app):

    for blueprint in app.config['BLUEPRINTS']:
        bp = __import__('discussion.blueprints.%s' % blueprint, fromlist=[blueprint])
        api.register_blueprint(getattr(bp, 'bp'))


def configure_errorhandlers(app):

    #Regular errors that can be raised from within blueprints and app
    def handler(e):
        response = jsonify({
            "code": e.code,
            "status": e.name,
            "message": e.message,
            "errors": getattr(e, 'errors', None) or {}
        })
        response.status = e.code
        return response
    
    errors_file = __import__('discussion.utils.errors', fromlist=['errors'])
    for error in errors_file.__all__:
        app.register_error_handler(getattr(errors_file, error), handler)
    
    #Application-wide errors that are raised by flask application instance
    @app.errorhandler(404)
    def forbidden_page(e):
        return jsonify({
            "code": e.code,
            "status": e.name,
            "message": 'The page you are requesting does not exists.',
            "errors": {}
        })
    
    @app.errorhandler(405)
    def forbidden_page(e):
        return jsonify({
            "code": e.code,
            "status": e.name,
            "message": 'You have used wrong method.',
            "errors": {}
        })
    
    @app.errorhandler(500)
    def forbidden_page(e):
        logger.exception('')
        return jsonify({
            "code": e.code,
            "status": e.name,
            "message": 'We can not respond to your request due to some server problems.',
            "errors": {}
        })


def create_app(config_name='default'):

    app = Flask(__name__)
    
    configure_app(app, config_name)

    return app


def configure_app(app, config_name):

    app.config.from_object(config[config_name])
    
    configure_logging(app)

    configure_extentions(app)

    configure_blueprints(app)
    
    configure_errorhandlers(app)


def configure_extentions(app):

    db.init_app(app)
    
    migrate.init_app(app, db)
    
    marshmallow.init_app(app)
    
    api.init_app(app)
