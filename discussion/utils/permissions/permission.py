from functools import wraps

import jwt
from flask import current_app, g, request, jsonify
from datetime import datetime, timedelta
from discussion.errors import InvalidCredentials, InvalidToken, JsonPermissionDenied
from discussion.models.tokenblacklist import TokenBlackList
from discussion.models.user import User





def str_to_class(classname):
    module = __import__('discussion.permissions', fromlist=['permissions'])
    return getattr(module, classname)



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
                raise JsonPermissionDenied(f"Premission {permission_class} required.")
            if shouldnt_have is not None:
                for permission_class in shouldnt_have:
                    permission = str_to_class(permission_class)()
                    if permission.has_access(**kwargs):
                        raise JsonPermissionDenied(f"Premission {permission_class} required.")
            return f(*args, **kwargs)
        return decorator
    return wraper_function