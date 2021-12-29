from flask import Blueprint
from flask_httpauth import HTTPBasicAuth
from flask import g
from discussion.models import User

auth_bp = Blueprint('auth', __name__)

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.password_check(password):
        return False
    g.user = user
    return True
