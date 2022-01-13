from flask_smorest import Blueprint

bp = Blueprint('unfollow', 'unfollows', __name__, url_prefix='/unfollows')

from . import views