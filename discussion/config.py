import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))



log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(name)s] - [%(asctime)s] - [%(levelname)s] - [%(filename)s/%(module)s/%(funcName)s/%(lineno)d] - [%(message)s]'
        },
        # 'request': {
        #     '()': 'discussion.utils.formatters.RequestFormatter',
        #     'format': '[%(name)s] - [%(asctime)s] - [%(method)s] - [%(url)s] - [%(remote_addr)s] - [%(user_agent)s] - [%(authorization)s]',
        # },
        'response': {
            '()': 'discussion.utils.formatters.ResponseFormatter',
            'format': '[%(name)s] - [%(asctime)s] - [%(method)s] - [%(url)s] - [%(remote_addr)s] - [%(user_agent)s] - [%(authorization)s]- [%(status)s]',
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
        'api_handler': {
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
        'api_logger': {
            'level': 'INFO',
            'handlers': ['api_handler'],
            'propagate': False,
        },
        # 'sqlalchemy.engine': {
        #     'level': 'INFO',
        #     'handlers': ['main_log_handler'],
        #     'propagate': False,
        # }
    },
    'root': {
        'level': 'NOTSET',
        'handlers': ['main_log_handler']
    }
}


class Config:

    #Secret key
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
    MAX_SESSIONS = 5
    
    #Token EXP
    ACCESS_TOKEN_EXP = timedelta(seconds=600)
    REFRESH_TOKEN_EXP = timedelta(days=365)

    #Swagger documentation
    API_TITLE = "Discussion API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = '/doc'
    OPENAPI_REDOC_PATH = '/redoc'
    OPENAPI_SWAGGER_UI_PATH = '/swagger'
    OPENAPI_SWAGGER_UI_URL = 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.19.5/'


    # #Pagination
    # DISCUSSION_DISCUSSIONS_PER_PAGE = 3
    # DISCUSSION_POSTS_PER_PAGE = 5
    # DISCUSSION_INVITATIONS_PER_PAGE = 10
    
    #Database
    DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME', 'dana')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 32343234)
    DBNAME = 'discussionapp'
    PORT = 5432
    HOST = "localhost"
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{HOST}:{PORT}/{DBNAME}"

    #Logging config
    LOG_CONFIG = log_config

    #Redis
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_DECODE_RESPONSES = True

    #Caching
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 1




class DevelopementConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'dev_database.db')


class TestingConfig(Config):
    TESTING = True

    MAX_SESSIONS = 1

    REDIS_DB = 1

    DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME', 'dana')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 32343234)
    DBNAME = 'test_discussionapp'
    PORT = 5432
    HOST = "localhost"
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    # SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'test_database.db')


class ProcudtionConfig(Config):
    pass

config = {
    'development': DevelopementConfig,
    'testing': TestingConfig,
    'production': ProcudtionConfig,

    'default': DevelopementConfig
}