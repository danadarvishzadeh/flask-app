from uuid import uuid4

from itsdangerous import exc


from discussion.models.user import User
from flask import current_app, g
from discussion.utils.errors import InvalidToken
from discussion.extentions import redis

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
        return g.access_token
    except:
        return None

def extract_refresh_token(body):
    try:
        refresh_token = body.get('refresh_token')
        g.refresh_token = refresh_token
        return refresh_token
    except:
        return None

def clear_token():
    redis.connection.delete(g.user.last_token)
    g.user.update({'last_token': ''})

def check_tokens_with_redis(access_token, refresh_token):
    g.ac_user_id, g.rf_user_id = redis.connection.mget(access_token, refresh_token)

def load_user_for_refreshing():
    if not g.rf_user_id:
        raise InvalidToken('')
    user = User.query.get(g.rf_user_id)
    if g.rf_user_id != g.ac_user_id\
        or user.last_token != g.access_token:
        raise InvalidToken('')
    g.user = user

def load_user_from_access_token():
    if not g.ac_user_id:
        raise InvalidToken('')
    g.user = User.query.get(g.ac_user_id)