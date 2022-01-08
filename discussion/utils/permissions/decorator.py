from functools import wraps

import jwt
from flask import g, request, jsonify
from discussion.errors import JsonPermissionDenied





def str_to_class(classname):
    module = __import__('discussion.permissions', fromlist=['permissions'])
    return getattr(module, classname)



def permission_required(resource, required=None, one_of=None, forbidden=None):
    def wraper_function(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            if required is not None:
                for permission_class in required:
                    permission = str_to_class(permission_class)()
                    if not permission.has_access(resource, **kwargs):
                        raise JsonPermissionDenied(f"Premission {permission_class} required.")
            if one_of is not None:
                for permission_class in one_of:
                    permission = str_to_class(permission_class)()
                    if permission.has_access(**kwargs):
                        return f(*args, **kwargs)
                raise JsonPermissionDenied(f"Premission {permission_class} required.")
            if forbidden is not None:
                for permission_class in forbidden:
                    permission = str_to_class(permission_class)()
                    if permission.has_access(**kwargs):
                        raise JsonPermissionDenied(f"Premission {permission_class} required.")
            return f(*args, **kwargs)
        return decorator
    return wraper_function