import logging
from datetime import datetime
from functools import wraps

from discussion.models.user import User
from discussion.utils.errors import InvalidAttemp, InvalidToken
from discussion.utils.util import (create_token_pair, depricate_all_tokens,
                                   extract_access_token, extract_refresh_token,
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
    depricate_all_tokens(owner_id=g.user.id)
    g.user.update(data={'last_login': datetime.utcnow()})
    return create_token_pair()

def logout():
    try:
        access_token = extract_access_token(request.headers)
        load_user_from_access_token(access_token)
        depricate_all_tokens(access_token=access_token)
        g.user.update_last_seen()
    except (InvalidToken, AttributeError, IndexError):
        logger.warning(f"logout attemp with invalid token: {request.headers.get('Authorization')}")


def refresh_user_token():
    g.access_token.update({'is_active': False})
    g.access_token.refresh_token[0].update({'is_active': False})
    return create_token_pair()


def token_required(refresh=False):
    def wrapper_function(f):  
        @wraps(f)
        def decorator(*args, **kwargs):        
            try:
                access_token = extract_access_token(request.headers)
                if not refresh:
                    load_user_from_access_token(access_token)
                else:
                    refresh_token = extract_refresh_token(request.get_json())
                    load_user_for_refreshing(access_token, refresh_token)
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
