from datetime import datetime, timedelta
from functools import wraps

import jwt
from discussion.errors import InvalidCredentials, InvalidToken
from discussion.models.tokenblacklist import TokenBlackList
from discussion.models.user import User
from flask import current_app, g, request


def encode_auth_token(user):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1, seconds=0),
        'iat': datetime.utcnow(),
        'sub': user.id
    }
    token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256').decode()
    while TokenBlackList.query.filter_by(token=token).first() is not None:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1, seconds=0),
            'iat': datetime.utcnow(),
            'sub': user.id
        }
        token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256').decode()
    return token

def decode_auth_token(auth_token):
    if TokenBlackList.query.filter_by(token=auth_token).first() is not None:
        return None
    payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
    user = User.query.get(payload['sub'])
    return user

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            token = request.headers.get('Authorization').split()[1]
            user = decode_auth_token(token)
            if user is None:
                raise InvalidCredentials(message='You provided an invalid token.')
            g.user = user
        except IndexError:
            raise InvalidCredentials(message='You did not provided a token.')
        except AttributeError as e:
            raise InvalidCredentials(message='You did not provided a token.')
        except jwt.InvalidTokenError:
            raise InvalidToken('You have submitted an invalid token.')
        except jwt.ExpiredSignatureError:
            raise InvalidToken('You have submitted an expired token.')
        else:
          return f(*args, **kwargs)
    return decorator
