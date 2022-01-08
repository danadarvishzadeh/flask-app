from functools import wraps

import jwt
from flask import g, request, jsonify
from discussion.utils.errors import JsonPermissionDenied





def str_to_class(classname):
    module = __import__('discussion.utils.perms.permissions', fromlist=['permissions'])
    return getattr(module, classname)



def permission_required(resource, required_permissions=None, one_of=None, forbidden_permissions=None):
    def wraper_function(f):
        @wraps(f)
        def decorator(*args, **kwargs):

            #raise error if one of the requirement permissions is not satisfied
            if required_permissions is not None:
                for permission_class in required_permissions:
                    permission = str_to_class(permission_class)()
                    if not permission.has_access(resource, **kwargs):
                        raise JsonPermissionDenied(f"Premission {permission_class} required.")
            
            #raise error if none of the one_of permissions is satisfied
            if one_of is not None:
                for permission_class in one_of:
                    permission = str_to_class(permission_class)()
                    if permission.has_access(resource, **kwargs):
                        return f(*args, **kwargs)
                raise JsonPermissionDenied(f"Premission {permission_class} required.")
            
            #raise error if one of the forbidden permissions is met
            if forbidden_permissions is not None:
                for permission_class in forbidden_permissions:
                    permission = str_to_class(permission_class)()
                    if permission.has_access(resource, **kwargs):
                        raise JsonPermissionDenied(f"Premission {permission_class} required.")

            return f(*args, **kwargs)
        return decorator
    return wraper_function