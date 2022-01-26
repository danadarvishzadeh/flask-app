import logging
from functools import wraps
from discussion.extentions import redis
from discussion.models.user import User
from discussion.utils.errors import InvalidAttemp, InvalidToken, SessionMismatch, SessionLimitReached
from discussion.utils.util import (create_token_pair, extract_access_token,
                                   extract_refresh_token,
                                   load_user_from_access_token,
                                   load_user_from_refresh_token, Session)
from flask import g, request, current_app

logger = logging.getLogger(__name__)


def authenticate(creadentials):
    if 'username' in creadentials and 'password' in creadentials:
        username = creadentials['username']
        password = creadentials['password']
        user = User.query.filter(User.username==username, User.is_active==True).first()
        if user and user.password_check(password):
            g.user = user
            g.session = Session()
            return True
    return False

def login():
    g.user.update_last_login()
    if g.session.sessions_limit_exceeded():
        raise SessionLimitReached()
    return create_token_pair()

def central_logout():
    pipe = redis.connection.pipeline()

    for a, r in g.session.get_all_tokens():
        pipe = pipe.delete(a).delete(r)
    
    pipe = pipe.delete(g.user.id)
    pipe = pipe.delete(g.access_token)
    pipe.execute()
    g.user.update_last_seen()

def extend_token_expire_time():
    g.session.renew_token()

def device_logout():
    g.session.delete_session()
    g.user.update_last_seen()

def refresh_user_token():
    return create_token_pair()


def token_required(refresh=False):
    def wrapper_function(f):  
        @wraps(f)
        def decorator(*args, **kwargs):        
            try:
                if not refresh:
                    extract_access_token(request.headers)
                    load_user_from_access_token()
                else:
                    extract_refresh_token(request.get_json())
                    load_user_from_refresh_token()
            except (InvalidToken, AttributeError, IndexError):
                logger.warning(f"login attemp with invalid token: {request.headers.get('Authorization')}")
                raise InvalidToken('invalid token.')
            except SessionMismatch as e:
                logger.warning(f"login attemp with token mismatch: {request.headers.get('Authorization')}")
                raise InvalidToken('invalid token.')
            except Exception as e:
                logger.exception('')
                raise InvalidAttemp()
            else:
                return f(*args, **kwargs)
        return decorator
    return wrapper_function
