import os


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jifaor24t5g249gjeomf'
    
    #Blueprints
    BLUEPRINTS = (
        'users',
        'discussions',
        'posts',
        'follows',
        'unfollows',
        'invites',
    )
    

    #SQLAlchemy
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    

    #Documentation
    API_TITLE = "Discussion API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = '/doc'
    OPENAPI_REDOC_PATH = '/redoc'
    OPENAPI_SWAGGER_UI_PATH = '/swagger'
    # The following is equivalent to OPENAPI_SWAGGER_UI_VERSION = '3.19.5'
    OPENAPI_SWAGGER_UI_URL = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.19.5/'


    #Pagination
    DISCUSSION_DISCUSSIONS_PER_PAGE = 3
    DISCUSSION_POSTS_PER_PAGE = 5
    DISCUSSION_INVITATIONS_PER_PAGE = 10
    

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

class ErrorFilter:
    def __init__(self, name=''):
        self.name = name

    def filter(self, record):
        return record.level == 'error'

#formatter class key is used for custome formatters
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(name)s] - [%(asctime)s] - [%(levelname)s] %(message)s'
        },
        'advance': {
            'format': '[%(name)s] - [%(asctime)s] - [%(levelname)s]----%(filename)s---%(module)s-%(funcName)s-%(lineno)d: %(message)s'
        },
        'simple': {
            'format': '[%(name)s] - [%(asctime)s]  %(message)s'
        },
        'request': {
            '()': 'discussion.utils.logging.RequestFormatter',
            'format': '[%(name)s] - [%(asctime)s] - [%(method)s] - [%(url)s] - [%(remote_addr)s] - [%(user_agent)s] - [%(authorization)s]',
        },
        'response': {
            '()': 'discussion.utils.logging.ResponseFormatter',
            'format': '[%(name)s] - [%(asctime)s] - [%(status)s]',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'main_log_handler': {
            'level': 'INFO',
            'formatter': 'advance',
            'class': 'logging.FileHandler',
            'filename': 'log.txt',
        },
        'request_handler': {
            'level': 'INFO',
            'formatter': 'request',
            'class': 'logging.FileHandler',
            'filename': 'log.txt'
        },
        'response_handler': {
            'level': 'INFO',
            'formatter': 'response',
            'class': 'logging.FileHandler',
            'filename': 'log.txt'
        },
    },
    'loggers': {
        'werkzeug': {
            'level': 'NOTSET',
            'handlers': ['console'],
            'propagate': False,
        },
        'request_logger': {
            'level': 'INFO',
            'handlers': ['request_handler',],
            'propagate': False,
        },
        'response_logger': {
            'level': 'INFO',
            'handlers': ['response_handler',],
            'propagate': False,
        },
    },
    'root': {
        'level': 'NOTSET',
        'handlers': ['main_log_handler']
    }
}