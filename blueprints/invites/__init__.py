from flask import Blueprint 
import logging

bp = Blueprint('invites', __name__, url_prefix='/invites')

logger = logging.getLogger(bp.name)

from . import views