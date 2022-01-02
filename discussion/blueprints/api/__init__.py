from flask import Blueprint 
import logging

bp = Blueprint('api', __name__)

logger = logging.getLogger(bp.name)

from . import views