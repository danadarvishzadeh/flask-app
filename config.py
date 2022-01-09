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
        'follow',
        'unfollow',
        'invite',
    )

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

template = {
    "swagger": "2.0",
    "info": {
        "title": "Discussion API",
        "description": "API for discussion app",
        "version": "1.0.0"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": [
        "http",
    ],
    "definitions":{
        "Discussion": {
            "type": "object",
            "properties":{
                "discussion_id":{
                    "type": "integer"
                },
                "creator_id":{
                    "type": "integer"
                },
                "title":{
                    "type": "string"
                },
                "description":{
                    "type": "string"
                },
                "date_created":{
                    "type": "string",
                    "format": "date-time"
                },
                "followed_by": {
                    "$ref": "#/definitions/Follow"
                },
                "invitations": {
                    "$ref": "#/definitions/Invitation"
                },
                "creator":{
                    "$ref": "#/definitions/User"
                },
                "posts": {
                    "$ref": "#/definitions/Post"
                },
                "participants": {
                    "$ref": "#/definitions/Participate"
                },
            },
        },
        "Follow": {
            "type": "object",
            "properties": {
                "follower_id": {
                    "type": "integer"
                },
                "discussion_id": {
                    "type": "integer"
                },
                "started_following": {
                    "type": "string",
                    "format": "date-time"
                },
            },
        },
        "Invitation": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "inviter_id": {
                    "type": "integer"
                },
                "invited_id": {
                    "type": "integer"
                },
                "discussion_id": {
                    "type": "integer"
                },
                "date_sent": {
                    "type": "string",
                    "format": "date-time"
                },
                "body": {
                    "type": "string",
                },
                "status": {
                    "type": "string",
                },
            },
        },
        "Participate": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "host_id": {
                    "type": "integer"
                },
                "participant_id": {
                    "type": "integer"
                },
                "discussion_id": {
                    "type": "integer"
                },
                "date_started": {
                    "type": "string",
                    "format": "date-time"
                },
            },
        },
        "Post": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "author_id": {
                    "type": "integer"
                },
                "discussion_id": {
                    "type": "integer"
                },
                "date_created": {
                    "type": "string",
                    "format": "date-time"
                },
                "body": {
                    "type": "string",
                },
            },
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "email": {
                    "type": "string",
                },
                "username": {
                    "type": "string",
                },
                "name": {
                    "type": "string",
                },
                "lastname": {
                    "type": "string",
                },
                "created_discussions": {
                    "$ref": "#/definitions/Discussion"
                },
                "posts": {
                    "$ref": "#/definitions/Post"
                },
                "invitations_sent": {
                    "$ref": "#/definitions/Invitation"
                },
                "invitations_recived": {
                    "$ref": "#/definitions/Invitation"
                },
                "host_for": {
                    "$ref": "#/definitions/Participate"
                },
                "participated_with_users": {
                    "$ref": "#/definitions/Participate"
                },
            },
        },
    },
}