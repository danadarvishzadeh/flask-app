from flask import Blueprint 
import logging

bp = Blueprint('discussion', __name__, url_prefix='/discussions')

logger = logging.getLogger(bp.name)

from . import views