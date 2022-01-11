import logging
from flask_smorest import Blueprint

bp = Blueprint('post', 'posts', __name__, url_prefix='/posts')

logger = logging.getLogger(bp.name)

from . import views