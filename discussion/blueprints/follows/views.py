import traceback

from discussion.app import db
from discussion.blueprints.follows import bp
from discussion.models.discussion import Discussion
from discussion.models.follow import Follow
from discussion.utils.auth import token_required
from discussion.utils.errors import InvalidAttemp, JsonIntegrityError, ResourceDoesNotExists
from discussion.utils.permissions.decorators import permission_required
from flask import g
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

@bp.route('/<int:discussion_id>', methods=["POST"])
class FollowView(MethodView):

    @token_required
    @permission_required(Discussion, forbidden_permissions=["IsOwner", "InPartners"])
    @bp.response(204)
    def post(self, discussion_id):
        try:
            Follow(owner_id=g.user.id, discussion_id=discussion_id).save()
            logger.info(f'{g.user.username} followed discussion_id {discussion_id}')
        except IntegrityError as e:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except ResourceDoesNotExists:
            logger.warning(f'Resource does not exists.')
            raise ResourceDoesNotExists()
        except Exception as e:
            logger.exception('')
            raise InvalidAttemp()
