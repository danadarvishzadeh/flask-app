from functools import wraps

import jwt
from flask import g, request, jsonify
from discussion.utils.errors import JsonPermissionDenied





def str_to_class(classname, **kwargs):
    module = __import__('discussion.utils.permissions.permissions', fromlist=['permissions'])
    return getattr(module, classname)(kwargs)



def permission_required(resource, store_resource=True, required_permissions=None, one_of=None, forbidden_permissions=None):
    def wraper_function(f):
        @wraps(f)
        def decorator(*args, **kwargs):

            #raise error if one of the requirement permissions is not satisfied
            if required_permissions is not None:
                for permission_class in required_permissions:
                    
                    permission = str_to_class(permission_class, resource=resource, store_resource=store_resource)
                    
                    if not permission.has_access():
                        raise JsonPermissionDenied(f"Premission {permission_class} required.")
            
            #raise error if none of the one_of permissions is satisfied
            if one_of is not None:
                for permission_class in one_of:
                    
                    permission = str_to_class(permission_class, resource=resource, store_resource=store_resource)
                    
                    if permission.has_access():
                        return f(*args, **kwargs)
                raise JsonPermissionDenied(f"Premission {permission_class} required.")
            
            #raise error if one of the forbidden permissions is met
            if forbidden_permissions is not None:
                for permission_class in forbidden_permissions:
                    
                    permission = str_to_class(permission_class, resource=resource, store_resource=store_resource)
                    
                    if permission.has_access():
                        raise JsonPermissionDenied(f"Premission {permission_class} required.")

            return f(*args, **kwargs)
        return decorator
    return wraper_function