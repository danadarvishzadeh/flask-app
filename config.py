import os


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jifaor24t5g249gjeomf'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DISCUSSION_DISCUSSIONS_PER_PAGE = 3
    DISCUSSION_POSTS_PER_PAGE = 5
    DISCUSSION_INVITATIONS_PER_PAGE = 10
    BLUEPRINTS = (
        'users',
        'discussions',
        'posts',
        'follows',
        'unfollows',
        'invites',
    )
    API_TITLE = "Discussion API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = '/doc'
    OPENAPI_REDOC_PATH = '/redoc'
    OPENAPI_SWAGGER_UI_PATH = '/swagger'
    # The following is equivalent to OPENAPI_SWAGGER_UI_VERSION = '3.19.5'
    OPENAPI_SWAGGER_UI_URL = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.19.5/'
    
    @staticmethod
    def init_app(app):
        pass


class DevelopementConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'dev_database.db')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'test_database.db')


# class ProcudtionConfig(Config):
#     DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
#     DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
#     DBNAME = 'DiscussionApp'
#     POST = 12345
#     HOST = "123.123.123.123"
#     SQLALCHEMY_DATABASE_URI = os.environ.get(
#         f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{HOST}:{PORT}/{DBNAME}"
#         )
#     @classmethod
#     def init_app(cls, app):
#         Config.init_app(app)


config = {
    'development': DevelopementConfig,
    'testing': TestingConfig,
    # 'production': ProcudtionConfig,

    'default': DevelopementConfig
}

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    #     'debug': {
    #         'level': 'DEBUG',
    #         'formatter': 'standard',
    #         'class': 'logging.handlers.RotatingFileHandler',
    #         'filename': './discussion/logs/debug.log',
    #         'maxBytes': 1000000,
    #         'backupCount': 3,
    #     },
    #     'error': {
    #         'level': 'ERROR',
    #         'formatter': 'standard',
    #         'class': 'logging.handlers.RotatingFileHandler',
    #         'filename': './discussion/logs/error.log',
    #         'maxBytes': 1000000,
    #         'backupCount': 3,
    #     },
    },
    # 'loggers': {
    #     '': {
    #         'handlers': ['console'],
    #         'level': 'DEBUG',
    #         'propagate': True
    #     },
    #     'discussions': {
    #         'handlers': ['debug', 'error'],
    #         'level': 'DEBUG',
    #         'propagate': True
    #     },
    #     'posts': {
    #         'handlers': ['debug', 'error'],
    #         'level': 'DEBUG',
    #         'propagate': True
    #     },
    #     'users': {
    #         'handlers': ['debug', 'error'],
    #         'level': 'DEBUG',
    #         'propagate': True
    #     },
    #     'follow': {
    #         'handlers': ['debug', 'error'],
    #         'level': 'DEBUG',
    #         'propagate': True
    #     },
    #     'invite': {
    #         'handlers': ['debug', 'error'],
    #         'level': 'DEBUG',
    #         'propagate': True
    #     },
    # },
}