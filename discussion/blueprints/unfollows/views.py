import traceback

from discussion.blueprints.unfollows import bp
from discussion.models.follow import Follow
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.utils.auth import token_required
from discussion.utils.errors import InvalidAttemp, ResourceDoesNotExists
from discussion.utils.permissions.decorators import permission_required
from flask import g, jsonify
from flask.views import MethodView
import logging

logger = logging.getLogger(__name__)

@bp.route('/<int:discussion_id>', methods=['DELETE'])
class UnfollowView(MethodView):

    @token_required
    @bp.response(204)
    def delete(self, discussion_id):
        try:
            Follow.query.filter_by(discussion_id=discussion_id, owner_id=g.user.id).first().delete()
            logger.info(f'{g.user.username} unfollowed discussion_id {discussion_id}')
        except AttributeError as e:
            print(e)
            logger.warning(f'Resource does not exists.')
            raise ResourceDoesNotExists()
        except:
            logger.exception('')
            raise InvalidAttemp()