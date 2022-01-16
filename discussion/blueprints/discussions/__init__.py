from flask_smorest import Blueprint

bp = Blueprint('discussions', 'discussions', __name__, url_prefix='/discussions')


from . import views