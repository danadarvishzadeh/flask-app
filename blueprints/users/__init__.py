import logging
from flask_smorest import Blueprint

bp = Blueprint('user', 'users', __name__, url_prefix='/users')

logger = logging.getLogger(__name__)

from . import views