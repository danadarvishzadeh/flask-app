from flask import Blueprint
from flask_httpauth import HTTPBasicAuth
from flask import g, request, jsonify
from discussion.models import User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# auth = HTTPBasicAuth()


# @auth.verify_password
# def verify_password(username, password):
#     user = User.query.filter_by(username=username).first()
#     if not user or not user.password_check(password):
#         return False
#     g.user = user
#     return True


@auth_bp.route('/users/login/', methods=['POST'])
def login_user():
    try:
        auth_token = request.headers.get('Authorization').split()[1]
        user = User.decode_auth_token(auth_token)
        if user:
            return jsonify({
                'message': 'you are currently logged in.'
            })
    except Exception:
        pass
    req_json = request.get_json()
    if not 'username' in req_json and not 'password' in req_json:
        return jsonify(
            {
                'error': 'could not verify.'
            }
        ), 401
    user = User.query.filter_by(username=req_json['username']).first()
    if user.password_check(req_json['password']):
        try:
            token = user.encode_auth_token()
            print(token)
            return jsonify({
                'token': token.encode("utf-8")
            })
        except Exception as e:
            print(e)
            pass

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            token = request.headers.get('Authorization').split()[1]
            user = User.decode_auth_token(header)
            g.user = user
            return f(*args, **kwargs)
        except IndexError:
            return jsonify(
            {
                'error': 'bad token.'
            }
        ), 401
        except Exception as e:
            return e
    return decorator

@auth_bp.route('/users/logout/', methods=['POST'])
def log_out():
    token = request.headers.get('Authorization').split()[1]
