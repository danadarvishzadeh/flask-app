from discussion.app import db
from discussion.blueprints.follows import bp, logger
from discussion.utils.errors import (ActionIsNotPossible, InvalidAttemp,
                               JsonIntegrityError, JsonValidationError,
                               ResourceDoesNotExists)
from discussion.models.follow import Follow
from discussion.utils.permissions.decorators import permission_required
from discussion.utils.auth import token_required
from flask import g, jsonify
from discussion.models.discussion import Discussion
from sqlalchemy.exc import IntegrityError
import traceback
from flasgger import SwaggerView
from discussion.schemas.response import ErrorSchema, OkResponse


class UnfollowView(SwaggerView):
    decorators = [
        token_required,
    ]
    parameters = [
        {
            "in": "path",
            "name": "discussion_id",
            "type": "string"
        }
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
    def delete(self, discussion_id):
        follow = Follow.query.filter_by(discussion_id=discussion_id).first()
        if follow:
            if follow.owner_id == g.user.id:
                follow.delete()
                db.session.commit()
                return jsonify({'response': 'Ok!'}), 200
            else:
                raise InvalidAttemp()
        else:
            raise ResourceDoesNotExists()