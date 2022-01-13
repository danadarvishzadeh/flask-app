from flask_smorest import Blueprint

bp = Blueprint('discussion', 'discussions', __name__, url_prefix='/discussions')


from . import views