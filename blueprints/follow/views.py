from discussion.app import db
from discussion.blueprints.follow import bp, logger
from discussion.utils.errors import (ActionIsNotPossible, InvalidAttemp,
                               JsonIntegrityError, JsonValidationError,
                               ResourceDoesNotExists)
from discussion.models.follow import Follow
from discussion.utils.perms.decorators import permission_required
from discussion.utils.auth import token_required
from flask import g, jsonify
from discussion.models.discussion import Discussion
from sqlalchemy.exc import IntegrityError
import traceback
from flasgger import SwaggerView
from discussion.schemas.response import OkResponse
from discussion.schemas.response import ErrorSchema, OkResponse

class FollowView(SwaggerView):
    decorators = [
        token_required,
        permission_required(Discussion, forbidden_permissions=['IsOwner'])
    ]
    responses = {
        200: {
            "description": "successful.",
            "schema": OkResponse
        },
        400: {
            "description": "Invalid input.",
            "schema": ErrorSchema
        },
        500: {
            "description": "Invalid attemp.",
            "schema": ErrorSchema
        },
    }
    def post(self, discussion_id):
        follow = Follow.query.filter_by(partner_id=g.user.id, discussion_id=discussion_id).first()
        discussion = Discussion.query.get(discussion_id)
        try:
            follow = Follow()
            follow.partner_id = g.user.id
            follow.discussion_id = discussion_id
            db.session.add(follow)
            db.session.commit()
            return jsonify({'response': 'Ok!'}), 200
        except IntegrityError:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
