import logging
from flask_smorest import Blueprint

bp = Blueprint('invite', 'invites', __name__, url_prefix='/invites')

logger = logging.getLogger(bp.name)

from . import views