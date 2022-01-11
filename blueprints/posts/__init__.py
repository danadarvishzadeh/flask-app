import logging
from flask_smorest import Blueprint

bp = Blueprint('post', 'posts', __name__, url_prefix='/posts')

logger = logging.getLogger(__name__)

from . import views