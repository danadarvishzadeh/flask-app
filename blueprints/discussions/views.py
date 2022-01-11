import traceback

from discussion.app import db
from discussion.blueprints.discussions import bp, logger
from discussion.models.discussion import Discussion
from discussion.models.post import Post
from discussion.schemas.discussion import CreateDiscussionSchema, DiscussionSchema, EditDiscussionSchema
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.utils.auth import token_required
from discussion.utils.errors import (ActionIsNotPossible, InvalidAttemp,
                                     JsonIntegrityError,
                                     ResourceDoesNotExists)
from discussion.utils.permissions.decorators import permission_required
from flask.views import MethodView
from flask import g, jsonify, request
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError



@bp.route('/', methods=['POST'])
class DiscussionView(MethodView):

    @token_required
    @bp.arguments(CreateDiscussionSchema)
    def post(self, creation_data):
        try:
            creation_data.update({'owner_id': g.user.id})
            return jsonify(DiscussionSchema().dump(Discussion(**creation_data).save()))
        except IntegrityError as e:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()


@bp.route('/<int:discussion_id>', methods=['GET', 'PUT', 'DELETE'])
class DiscussionDetailView(MethodView):

    def get(self, discussion_id):
        discussion = Discussion.query.get(discussion_id)
        if discussion:
            return jsonify(DiscussionSchema().dump(discussion))
        logger.warning(f"Trying to access non-existing discussion with id {discussion_id}")
        raise ResourceDoesNotExists()

    @token_required
    @permission_required(Discussion, required_permissions=["IsOwner"])
    @bp.arguments(EditDiscussionSchema)
    def put(self, update_data, discussion_id):
        try:
            g.resource.update(update_data)
        except IntegrityError:
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    
    @token_required
    @permission_required(Discussion, required_permissions=["IsOwner"])
    def delete(self, discussion_id):
        g.resource.delete()