from flask import Blueprint 
import logging

bp = Blueprint('invite', __name__, url_prefix='/invite')

logger = logging.getLogger(bp.name)

from . import schemas
from . import views