import logging
from flask_smorest import Blueprint

bp = Blueprint('discussion', 'discussions', __name__, url_prefix='/discussions')

logger = logging.getLogger(__name__)

from . import views