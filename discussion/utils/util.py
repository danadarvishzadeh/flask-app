from uuid import uuid4
from weakref import ref

from discussion.models.access_token import AccessToken
from discussion.models.refresh_token import RefreshToken
from flask import current_app, g
from discussion.utils.errors import InvalidToken

def rand_str():
    return uuid4().hex

def create_access_token():
    token = rand_str()
    token_info = {
        'token': token,
        'owner_id': g.user.id,
        'expires_in': current_app.config['ACCESS_TOKEN_EXP'],
    }
    g.access_token = AccessToken(**token_info).save()
    return token

def create_refresh_token():
    token = rand_str()
    token_info = {
        'token': token,
        'owner_id': g.user.id,
        'access_token_id': g.access_token.id,
        'expires_in': current_app.config['REFRESH_TOKEN_EXP'],
    }
    RefreshToken(**token_info).save()
    return token

def create_token_pair():
    return create_access_token(), create_refresh_token()

def access_token_sanitizer(access_token):
    data = access_token.split()
    if data[0] == 'Bearer':
        return data[1]
    return None

def extract_access_token(headers):
    try:
        access_token = headers.get('Authorization')
        access_token = access_token_sanitizer(access_token)
        access_token = AccessToken.query.filter_by(token=access_token).first()
        return access_token
    except:
        raise InvalidToken('')

def extract_refresh_token(body):
    try:
        refresh_token = body.get('refresh_token')
        return RefreshToken.query.filter_by(token=refresh_token).first()
    except:
        raise InvalidToken('')

def load_user_from_access_token(access_token):
    if access_token.has_expired:
        access_token.update({'is_active': False})
        raise InvalidToken
    g.user = access_token.owner

def different_owners(access_token, refresh_token):
    return refresh_token.owner_id != access_token.owner_id

def non_matching_tokens(access_token, refresh_token):
    return different_owners(access_token, refresh_token)\
        or refresh_token.access_token != access_token

def depricate_all_tokens(access_token=None, refresh_token=None, owner_id=None):
    AccessToken.depricate_tokens(owner_id or access_token.owner_id)
    try:
        if refresh_token and different_owners(access_token, refresh_token):
            RefreshToken.depricate_tokens(refresh_token.owner_id)
    except:
        pass

def load_user_for_refreshing(access_token, refresh_token):
    if access_token.is_invalid\
        or refresh_token.is_invalid\
            or non_matching_tokens(access_token, refresh_token):
        depricate_all_tokens(access_token=access_token, refresh_token=refresh_token)
        raise InvalidToken('')
    g.user = access_token.owner
    g.access_token = access_token
