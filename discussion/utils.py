import sys
from flask import current_app

def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)

def permission_required(should_have=None, one_of=None, shouldnt_have=None):
    def wraper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            if shouldn_have is not None:
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
    return wraper