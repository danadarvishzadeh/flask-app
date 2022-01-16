from flask_smorest import Blueprint

bp = Blueprint('follows', 'follows', __name__, url_prefix='/follows')


from . import views