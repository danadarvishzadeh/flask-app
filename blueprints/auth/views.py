from functools import wraps
from datetime import datetime, timedelta
import jwt
from discussion.app import db
from discussion.models import TokenBlackList, User
from flask import abort, g, jsonify, request, current_app
from discussion.blueprints.auth import bp, logger
from discussion.blueprints.auth.errors import *
from discussion.blueprints.api.errors import InvalidAttemp
import traceback

def decode_auth_token(auth_token):
    payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
    user = User.query.get(payload['sub'])
    return user

def encode_auth_token(user):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1, seconds=0),
        'iat': datetime.utcnow(),
        'sub': user.id
    }
    token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256').decode()
    while TokenBlackList.query.filter_by(token=token).first():
        token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256').decode()
    return token

@bp.route('/users/login/', methods=['POST'])
def login_user():
    try:
        auth_token = request.headers.get('Authorization').split()[1]
        user = decode_auth_token(auth_token)
    except:
        pass
    else:
        if user is not None:
            logger.info(f"User {user.username} tried log in, having valid token.")
            raise InvalidCredentials(message='You have a already registered token and hence, logged in.')
        else:
            logger.info(f"User {user.username} tried log in, having invalid token.")
            raise InvalidCredentials(message='The Token you provided is invalid.')
    req_json = request.get_json()
    try:
        user = User.query.filter_by(username=req_json['username']).first()
        if user.password_check(req_json['password']):
            token = encode_auth_token(user)
            logger.info(f"User {user.username} logged in.")
            return jsonify({
                'token': token
            })
        else:
            raise InvalidCredentials(message='Username or Password you provided are invalid.')
    except AttributeError:
        raise InvalidCredentials(message='Please provide full creadentials.')
    except AttributeError:
        raise InvalidCredentials(message='Please provide full creadentials.')
        

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            token = request.headers.get('Authorization').split()[1]
            user = decode_auth_token(token)
            if user is None:
                raise InvalidCredentials(message='You provided an invalid token.')
            g.user = user
        except IndexError:
            raise InvalidCredentials(message='You did not provided a token.')
        except AttributeError as e:
            raise InvalidCredentials(message='You did not provided a token.')
        except jwt.InvalidTokenError:
            raise InvalidToken('You have submitted an invalid token.')
        except jwt.ExpiredSignatureError:
            raise InvalidToken('You have submitted an expired token.')
        else:
          return f(*args, **kwargs)
    return decorator

@bp.route('/users/logout/', methods=['POST'])
def logout_user():
    try:
        token = request.headers.get('Authorization').split()[1]
        decode_auth_token(token)
        tb = TokenBlackList(token=token)
        db.session.add(tb)
        db.session.commit()
        return jsonify({
            "response": "Ok!"
        })
    except IndexError:
        raise InvalidCredentials(message='You did not provided a token.')
    except jwt.DecodeError:
        raise InvalidToken('You have submitted an invalid token.')
    except AttributeError:
            raise InvalidCredentials(message='You did not provided a token.')
    except:
        trace_info = traceback.format_exc()
        logger.error(f"uncaught exception: {trace_info}")
        raise InvalidAttemp()
