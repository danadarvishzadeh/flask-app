from flask import Blueprint 
import logging

bp = Blueprint('follows', __name__, url_prefix='/follows')

logger = logging.getLogger(bp.name)

from . import views