from flask_smorest import Blueprint

bp = Blueprint('invite', 'invites', __name__, url_prefix='/invites')


from . import views