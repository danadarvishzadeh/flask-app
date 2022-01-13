from flask_smorest import Blueprint

bp = Blueprint('follow', 'follows', __name__, url_prefix='/follows')


from . import views