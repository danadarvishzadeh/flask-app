from flask import Blueprint 
import logging

bp = Blueprint('follow', __name__, url_prefix='/follow')

logger = logging.getLogger(bp.name)

from . import views