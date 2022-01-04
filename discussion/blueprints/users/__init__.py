from flask import Blueprint 
import logging

bp = Blueprint('users', __name__, url_prefix='/users')

logger = logging.getLogger(bp.name)

from . import schemas
from . import views