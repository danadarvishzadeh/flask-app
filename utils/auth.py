from datetime import datetime, timedelta
from functools import wraps

import jwt
from discussion.utils.errors import InvalidCredentials, InvalidToken
from discussion.models.tokenblacklist import TokenBlackList
from discussion.models.user import User
from flask import current_app, g, request


def encode_auth_token(user_id):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1, seconds=0),
        'iat': datetime.utcnow(),
        'sub': user_id
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
            if not user:
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

def authenticate(username, password):
    if username and password:
        user = User.query.filter_by(username=username).first()
        if not user:
            return False
        if not user.is_active:
            return False
        return user.password_check(password)
    else:
        return False

def login(username):
    user = User.query.filter_by(username=username).first()
    user.last_login = datetime.utcnow()
    user.save()
    return encode_auth_token(user.id)

def logout(user, token):
    splited_token = token.split()
    if len(splited_token) == 2:
        user.update_last_seen()
        TokenBlackList.depricate_token(token[1])
    else:
        raise InvalidToken()