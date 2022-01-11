import logging
from flask_smorest import Blueprint

bp = Blueprint('invite', 'invites', __name__, url_prefix='/invites')

logger = logging.getLogger(__name__)

from . import views