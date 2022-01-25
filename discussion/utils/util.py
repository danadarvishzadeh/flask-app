from uuid import uuid4

from discussion.utils.session import Session
from discussion.models.user import User
from flask import current_app, g, request
from discussion.utils.errors import InvalidToken, SessionMismatch
from discussion.extentions import redis
import logging

logger = logging.getLogger(__name__)


def rand_str():
    return uuid4().hex

def create_token_pair():
    ac, rf = rand_str(), rand_str()
    access_expire, refresh_expire = current_app.config['ACCESS_TOKEN_EXP'], current_app.config['REFRESH_TOKEN_EXP']
    redis.connection.pipeline().set(ac, g.user.id, access_expire).set(rf, g.user.id, refresh_expire).execute()
    g.user.update({'last_token': ac})
    return ac, rf

def access_token_sanitizer(access_token):
    data = access_token.split()
    if data[0] == 'Bearer':
        return data[1]
    return None

def extract_access_token(headers):
    try:
        access_token = headers.get('Authorization')
        g.access_token = access_token_sanitizer(access_token)
        g.access_user_id = redis.connection.get(g.access_token)
    except:
        g.access_token = None
        g.access_user_id = None

def extract_refresh_token(body):
    try:
        refresh_token = body.get('refresh_token')
        g.refresh_token = refresh_token
        g.refresh_user_id = redis.connection.get(g.refresh_token)
    except:
        g.refresh_token = None
        g.refresh_user_id = None

def create_token_pair():
    access_token, refresh_token = rand_str(), rand_str()
    
    access_token_expire = current_app.config['ACCESS_TOKEN_EXP']
    refresh_token_expire = current_app.config['REFRESH_TOKEN_EXP']
    
    pipe = redis.connection.pipeline()
    
    if g.session.refresh_token:
        pipe = pipe.delete(g.session.refresh_token)
        pipe = pipe.delete(g.session.access_token)

    g.session.refresh_token = refresh_token
    g.session.access_token = access_token
    
    pipe = pipe.mset({
        access_token: g.user.id,
        refresh_token: g.user.id
    })
    
    pipe = pipe.expire(access_token, access_token_expire)
    pipe = pipe.expire(refresh_token, refresh_token_expire)
    
    if g.session.index is not None:
        pipe = pipe.lset(g.user.id, g.session.index, str(g.session))
    else:
        pipe = pipe.rpush(g.user.id, str(g.session))
    
    pipe.execute()

    return access_token, refresh_token

def load_user_from_refresh_token():
    if not g.refresh_user_id:
        raise InvalidToken('')
    g.user = User.query.get(g.refresh_user_id)
    g.session = Session()
    if g.session.sessions_limit_exceeded():
        raise SessionMismatch()

def load_user_from_access_token():
    if not g.access_user_id:
        raise InvalidToken('')
    g.user = User.query.get(g.access_user_id)
    g.session = Session()
    if not g.session.current_session_exists():
        raise SessionMismatch()