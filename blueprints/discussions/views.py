import traceback

from discussion.app import db
from discussion.blueprints.discussions import bp, logger
from discussion.blueprints.discussions.paginators import DiscussionPaginator
from discussion.blueprints.posts.paginators import PostPaginator
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
from discussion.utils.perms.decorators import permission_required
from flasgger import SwaggerView
from flask import g, jsonify, request
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError


class DiscussionView(SwaggerView):
    tags = ['discussion']
    parameters = [
        {
            "name": "user_id",
            "description": "Id of user to filter discussions."
        },
        {
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
            paginator = DiscussionPaginator
            paginator.filters = {'owner_id': user_id}
            return DiscussionPaginator.return_page(page, 'get_creator_discussions')
        elif discussion_id is not None:
            discussion = Discussion.query.get(discussion_id)
            if discussion is not None:
                return jsonify(discussion_schema.dump(discussion))
            else:
                logger.warning(f"Trying to access non-existing discussion with id {discussion_id}")
                raise ResourceDoesNotExists()
        else:
            page = request.args.get('page', 1, type=int)
            return DiscussionPaginator.return_page(page, 'get_discussions')


class ChangeDiscussionView(SwaggerView):

    tags = ['discusison']
    decorators = [
        token_required,
        permission_required(Discussion,required_permissions=['IsOwner'])
    ]
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
            discussion.query.update(dict(data))
            db.session.commit()
            return jsonify(discussion_schema.dump(discussion))
        except ValidationError as e:
            raise JsonValidationError(e)
        except:
            trace_info = traceback.format_exc()
            print(logger)
            print(trace_info)
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    
    def delete(self, discussion_id):
        discussion = Discussion.query.get(discussion_id)
        discussion.query.delete()
        db.session.commit()
        return jsonify({'response': 'ok!'}), 200


class CreateDiscussionView(SwaggerView):

    tags = ['discussion']
    parameters = [
        {
            "in": "body",
            "name": "discussion",
            "type": "object",
            "schema": CreateDiscussionSchema
        }
    ]
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
            db.session.add(discussion)
            db.session.commit()
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
