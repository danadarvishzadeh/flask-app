from flask_smorest import Blueprint

bp = Blueprint('invites', 'invites', __name__, url_prefix='/invites')


from . import views