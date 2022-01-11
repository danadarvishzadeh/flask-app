import logging
from flask_smorest import Blueprint

bp = Blueprint('unfollow', 'unfollows', __name__, url_prefix='/unfollows')
logger = logging.getLogger(bp.name)

from . import views