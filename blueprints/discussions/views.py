import traceback

from discussion.app import db
from discussion.blueprints.discussions import bp, logger
from discussion.utils.paginators.discussion import DiscussionPaginator
from discussion.utils.paginators.post import PostPaginator
from discussion.models.discussion import Discussion
from discussion.models.post import Post
from discussion.schemas.discussion import (CreateDiscussionSchema,
                                           DiscussionSchema,
                                           create_discussion_schema,
                                           discussion_schema)
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.utils.auth import token_required
from discussion.utils.errors import (ActionIsNotPossible, InvalidAttemp,
                                     JsonIntegrityError, JsonValidationError,
                                     ResourceDoesNotExists)
from discussion.utils.permissions.decorators import permission_required
from flasgger import SwaggerView
from flask import g, jsonify, request
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError




class DiscussionCreationView(SwaggerView):

    tags = ['discussion']
    decorators = [
        token_required,
    ]
    parameters = [
        {
            "in": "body",
            "name": "discussion",
            "type": "object",
            "schema": CreateDiscussionSchema
        }
    ]
    security = {
        0: {
            "bearerAuth": []
        }
    }
    validate = True
    responses = {
        200: {
            "description": "Created discusison.",
            "schema": DiscussionSchema
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

    def post(self):
        req_json = request.get_json()
        try:
            discussion = create_discussion_schema.load(req_json)
            discussion.owner_id = g.user.id
            discussion.save()
            return jsonify(discussion_schema.dump(discussion))
        except ValidationError as e:
            raise JsonValidationError(e)
        except IntegrityError as e:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()


class DiscussionDetailView(SwaggerView):
    tags = ['discussion']
    parameters = [
        {
            "in": "path",
            "name": "user_id",
            "description": "Id of user to filter discussions."
        },
        {
            "in": "path",
            "name": "discussion_id",
            "description": "Id of discussion to be presented."
        },
    ]

    responses = {
        200: {
            "description": "Discussions detail.",
            "schema": DiscussionSchema
        },
        404: {
            "description": "requesting resource does not exists.",
            "schema": ErrorSchema
        },
    }

    def get(self, user_id, discussion_id):
        if user_id is not None:
            page = request.args.get('page', 1, type=int)
            paginator = DiscussionPaginator({'owner_id': user_id})
            return paginator.return_page(page, 'get_creator_discussions')
        elif discussion_id is not None:
            discussion = Discussion.query.get(discussion_id)
            if discussion:
                return jsonify(discussion_schema.dump(discussion))
            else:
                logger.warning(f"Trying to access non-existing discussion with id {discussion_id}")
                raise ResourceDoesNotExists()
        else:
            page = request.args.get('page', 1, type=int)
            return DiscussionPaginator().return_page(page, 'get_discussions')


class ChangeDiscussionView(SwaggerView):

    tags = ['discussion']
    decorators = [
        token_required,
        permission_required(Discussion,required_permissions=['IsOwner'])
    ]
    security = {
        0: {
            "bearerAuth": []
        }
    }
    parameters = [
        {
            "name": "discussion_id",
            "type": "integer",
            "in": "path"
        }
    ]
    validate = True
    responses = {
        200: {
            "description": "successful."
        },
        400: {
            "description": "invalid input."
        }
    }

    def put(self, discussion_id):
        """
        edit discussion details
        ---
        parameters:
            - in: body
              name: body
              type: string
            - in: body
              name: title
              type: string
        """
        discussion = Discussion.query.get(discussion_id)
        req_json = request.get_json()
        try:
            data = discussion_schema.load(req_json, partial=True)
            discussion.update(data)
            return jsonify(discussion_schema.dump(discussion))
        except ValidationError as e:
            raise JsonValidationError(e)
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    
    def delete(self, discussion_id):
        discussion = Discussion.query.get(discussion_id)
        discussion.delete()
        return jsonify({'response': 'ok!'}), 200


bp.add_url_rule('/',
                view_func=DiscussionCreationView.as_view('create_discussions'),
                methods=["POST"])

bp.add_url_rule('/',
                view_func=DiscussionDetailView.as_view('get_discussions'),
                methods=["GET"], defaults={'user_id': None, 'discussion_id': None})

bp.add_url_rule('/<int:discussion_id>/',
                view_func=DiscussionDetailView.as_view('get_discussion_detail'),
                methods=["GET"], defaults={'user_id': None})

bp.add_url_rule('/<int:user_id>/',
                view_func=DiscussionDetailView.as_view('get_user_discussions'),
                methods=["GET"], defaults={'discussion_id': None})

bp.add_url_rule('/<int:discussion_id>/',
                view_func=ChangeDiscussionView.as_view('edit_discussion_details'),
                methods=["PUT", "DELETE"])