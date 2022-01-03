from functools import wraps

import jwt
from flask import current_app, g, request

from discussion.errors import InvalidCredentials, InvalidToken, JsonPermissionDenied
from discussion.models.tokenblacklist import TokenBlackList
from discussion.models.user import User



def decode_auth_token(auth_token):
    payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
    user = User.query.get(payload['sub'])
    return user

def str_to_class(classname):
    module = __import__('discussion/%')
    return getattr(module, classname)

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
    while TokenBlackList.query.filter_by(token=token).first():
        token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256').decode()
    return token

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

def permission_required(should_have=None, one_of=None, shouldnt_have=None):
    def wraper_function(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            if shouldnt_have is not None:
                for permission_class in should_have:
                    permission = str_to_class(permission_class)()
                    if not permission.has_access(**kwargs):
                        raise JsonPermissionDenied(f"Premission {permission_class} required.")
            if one_of is not None:
                for permission_class in one_of:
                    permission = str_to_class(permission_class)()
                    if permission.has_access(**kwargs):
                        return f(*args, **kwargs)
            if shouldnt_have is not None:
                for permission_class in shouldnt_have:
                    permission = str_to_class(permission_class)()
                    if permission.has_access(**kwargs):
                        raise JsonPermissionDenied(f"Premission {permission_class} required.")
            return f(*args, **kwargs)
        return decorator
    return wraper_function
