import os

basedir = os.path.abspath(os.path.dirname(__file__))



log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(name)s] - [%(asctime)s] - [%(levelname)s]----%(filename)s---%(module)s-%(funcName)s-%(lineno)d: %(message)s'
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
            'formatter': 'default',
            'class': 'logging.StreamHandler',
        },
        'main_log_handler': {
            'level': 'INFO',
            'formatter': 'default',
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
    

    #Swagger documentation
    API_TITLE = "Discussion API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = '/doc'
    OPENAPI_REDOC_PATH = '/redoc'
    OPENAPI_SWAGGER_UI_PATH = '/swagger'
    # The following is equivalent to OPENAPI_SWAGGER_UI_VERSION = '3.19.5'
    # OPENAPI_SWAGGER_UI_URL = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.19.5/'
    OPENAPI_SWAGGER_UI_VERSION = '3.19.5'


    #Pagination
    DISCUSSION_DISCUSSIONS_PER_PAGE = 3
    DISCUSSION_POSTS_PER_PAGE = 5
    DISCUSSION_INVITATIONS_PER_PAGE = 10
    

    #Logging config
    LOG_CONFIG = log_config


class DevelopementConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'dev_database.db')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'test_database.db')


class ProcudtionConfig(Config):
    DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME', None)
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', None)
    DBNAME = 'DiscussionApp'
    PORT = 12345
    HOST = "123.123.123.123"
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    

config = {
    'development': DevelopementConfig,
    'testing': TestingConfig,
    'production': ProcudtionConfig,

    'default': DevelopementConfig
}