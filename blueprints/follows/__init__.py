import logging
from flask_smorest import Blueprint

bp = Blueprint('follow', 'follows', __name__, url_prefix='/follows')

logger = logging.getLogger(bp.name)

from . import views