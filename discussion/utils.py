from functools import wraps

import jwt
from flask import current_app, g, request, jsonify
from datetime import datetime, timedelta
from discussion.errors import InvalidCredentials, InvalidToken, JsonPermissionDenied
from discussion.models.tokenblacklist import TokenBlackList
from discussion.models.user import User



def decode_auth_token(auth_token):
    payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
    user = User.query.get(payload['sub'])
    return user

def str_to_class(classname):
    module = __import__('discussion.permissions', fromlist=['permissions'])
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
            if should_have is not None:
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


class PaginatorBase:
    
    filters = None
    query_set = None
    schema = None
    model = None
    output_name = None
    per_page = 5

    @classmethod
    def get_data_set(cls):
        if cls.query_set is not None:
            return cls.query_set
        data = cls.model.query
        if cls.filters is not None:
            data = data.filter_by(**cls.filters)
        return data

    @classmethod
    def return_page(cls, page, callback):
        pagination = cls.get_data_set().paginate(page, per_page=cls.per_page, error_out=False)
        data = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for(callback, page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for(callback, page=page+1, _external=True)
        output_name = cls.model.__name__.lower() + 's' if cls.output_name is None else cls.output_name
        return jsonify({
        output_name: cls.schema.dump(data, many=True),
        'prev': prev,
        'next': next,
        'count': pagination.total
        })