from flask import Blueprint 
import logging

bp = Blueprint('unfollows', __name__, url_prefix='/unfollows')

logger = logging.getLogger(bp.name)

from . import views