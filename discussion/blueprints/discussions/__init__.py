from flask_smorest import Blueprint

bp = Blueprint('discussions', 'discussions', __name__, url_prefix='/discussions')
bp.DEFAULT_PAGINATION_PARAMETERS = {"page": 1, "page_size": 10, "max_page_size": 100}

from . import views