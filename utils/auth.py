from datetime import datetime, timedelta
from functools import wraps

import jwt
from discussion.utils.errors import InvalidCredentials, InvalidToken
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
    return token

def decode_auth_token(auth_token):
    payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
    user = User.query.get(payload['sub'])
    return user

def token_required(f):
    
    @wraps(f)
    def decorator(*args, **kwargs):
        
        try:
            token = request.headers.get('Authorization').split()[1]
            user = decode_auth_token(token)
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

def authenticate(creadentials):
    if 'username' in creadentials and 'password' in creadentials:
        user = User.query.filter(User.username==username, User.is_active==True).first()
        if user and user.password_check(password):
            g.user = user
            return True
    return False

def login():
    g.user.update(data={'last_login': datetime.utcnow()})
    return encode_auth_token(g.user.id)

def logout(token):
    splited_token = token.split()
    if len(splited_token) == 2:
        g.user.update_last_seen()
        #TODO depricate token
    raise InvalidToken()