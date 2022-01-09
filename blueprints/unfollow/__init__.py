from flask import Blueprint 
import logging

bp = Blueprint('unfollow', __name__, url_prefix='/unfollow')

logger = logging.getLogger(bp.name)

from . import views