from flask_smorest import Blueprint

bp = Blueprint('user', 'users', __name__, url_prefix='/users')


from . import views