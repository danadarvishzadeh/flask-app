from flask_smorest import Blueprint

bp = Blueprint('posts', 'posts', __name__, url_prefix='/posts')


from . import views