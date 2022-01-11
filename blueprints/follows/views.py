import traceback

from discussion.app import db
from discussion.blueprints.follows import bp, logger
from discussion.models.discussion import Discussion
from discussion.models.follow import Follow
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.utils.auth import token_required
from discussion.utils.errors import (ActionIsNotPossible, InvalidAttemp,
                                     JsonIntegrityError,
                                     ResourceDoesNotExists)
from discussion.utils.permissions.decorators import permission_required
from flask import g, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError


@bp.route('/<int:discussion_id>', methods=["POST"])
class FollowView(MethodView):

    @token_required
    @permission_required(Follow, forbidden_permissions=["IsOwner", "InPartners"])
    @bp.response(204)
    def post(self, discussion_id):
        try:
            Follow({'owner_id': g.user.id, 'discussion_id': discussion_id}).save()
        except IntegrityError:
            db.session.rollback()
            raise JsonIntegrityError()
        except ResourceDoesNotExists:
            raise ResourceDoesNotExists()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
