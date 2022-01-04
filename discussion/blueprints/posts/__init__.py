from flask import Blueprint 
import logging

bp = Blueprint('posts', __name__, url_prefix='/posts')

logger = logging.getLogger(bp.name)

from . import schemas
from . import views