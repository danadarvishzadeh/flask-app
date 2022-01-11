import traceback

from discussion.blueprints.unfollows import bp, logger
from discussion.models.follow import Follow
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.utils.auth import token_required
from discussion.utils.errors import InvalidAttemp, ResourceDoesNotExists
from discussion.utils.permissions.decorators import permission_required
from flask import g, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError


@bp.route('/<int:discussion_id>', methods=['DELETE'])
class UnfollowView(MethodView):

    @token_required
    @permission_required(Follow, required_permissions=["IsOwner"])
    @bp.response(204)
    def delete(self, discussion_id):
        try:
            Follow.query.filter('discussion_id'==discussion_id, 'owner_id'==g.user.id).first().delete()
        except AttributeError:
            raise ResourceDoesNotExists()
        except:
            raise InvalidAttemp()