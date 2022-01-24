import logging
from datetime import datetime
from functools import wraps

from discussion.models.user import User
from discussion.utils.errors import InvalidAttemp, InvalidToken
from discussion.utils.util import (check_tokens_with_redis, clear_token,
                                   create_token_pair, extract_access_token,
                                   extract_refresh_token,
                                   load_user_for_refreshing,
                                   load_user_from_access_token)
from flask import g, request

logger = logging.getLogger(__name__)


def authenticate(creadentials):
    if 'username' in creadentials and 'password' in creadentials:
        username = creadentials['username']
        password = creadentials['password']
        user = User.query.filter(User.username==username, User.is_active==True).first()
        if user and user.password_check(password):
            g.user = user
            return True
    return False

def login():
    clear_token()
    g.user.update_last_login()
    return create_token_pair()

def logout():
    try:
        load_user_from_access_token()
        clear_token()
        g.user.update_last_seen()
    except (InvalidToken, AttributeError, IndexError):
        logger.warning(f"logout attemp with invalid token: {request.headers.get('Authorization')}")


def refresh_user_token():
    clear_token()
    return create_token_pair()


def token_required(refresh=False):
    def wrapper_function(f):  
        @wraps(f)
        def decorator(*args, **kwargs):        
            try:
                access_token = extract_access_token(request.headers) or ''
                refresh_token = extract_refresh_token(request.get_json()) or ''
                check_tokens_with_redis(access_token, refresh_token)
                if not refresh:
                    load_user_from_access_token()
                else:
                    load_user_for_refreshing()
            except (InvalidToken, AttributeError, IndexError):
                logger.warning(f"login attemp with invalid token: {request.headers.get('Authorization')}")
                raise InvalidToken('invalid token.')
            except Exception as e:
                logger.exception('')
                raise InvalidAttemp()
            else:
                return f(*args, **kwargs)
        return decorator
    return wrapper_function
