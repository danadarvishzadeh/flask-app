import traceback

from discussion.app import db
from discussion.blueprints.posts import bp, logger
from discussion.utils.paginators.post import PostPaginator
from discussion.models.discussion import Discussion
from discussion.models.post import Post
from discussion.schemas.post import (CreatePostSchema, PostSchema,
                                     create_post_schema, post_schema,
                                     post_schema)
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.utils.auth import token_required
from discussion.utils.errors import (InvalidAttemp, JsonIntegrityError,
                                     JsonValidationError,
                                     ResourceDoesNotExists)
from discussion.utils.permissions.decorators import permission_required
from flasgger import SwaggerView
from flask import g, jsonify, request
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from discussion.schemas.response import ErrorSchema, OkResponse

class PostView(SwaggerView):
    tags = ['post']
    parameters = [
        {
            "name": "discussion_id",
            "description": "Id of discussion to filter posts."
        },
        {
            "name": "post_id",
            "description": "Id of post to be presented."
        },
    ]

    responses = {
        200: {
            "description": "post detail.",
            "schema": PostSchema
        },
        404: {
            "description": "requesting resource does not exists.",
            "schema": ErrorSchema
        },
    }

    def get(self, discussion_id, post_id):
        if discussion_id is not None:
            page = request.args.get('page', 1, type=int)
            paginator = PostPaginator
            paginator.filters = {'discussion_id': discussion_id}
            return paginator.return_page(page, 'get_discussion_posts')
        elif discussion_id is not None:
            post = Post.query.get(post_id)
            if post:
                return jsonify(post_schema.dump(post))
            else:
                logger.warning(f"Trying to access non-existing post with id {post_id}")
                raise ResourceDoesNotExists()
        else:
            page = request.args.get('page', 1, type=int)
            return PostPaginator.return_page(page, 'get_posts')



class ChangePostView(SwaggerView):

    tags = ['post']
    decorators = [
        token_required,
        permission_required(Post,required_permissions=['IsOwner'])
    ]
    parameters = [
        {
            "name": "post_id",
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

    def put(self, post_id):
        """
        edit post details
        ---
        parameters:
            - in: body
              name: body
              type: string
        """
        post = Post.query.get(post_id)
        req_json = request.get_json()
        try:
            data = post_schema.load(req_json, partial=True)
            post.query.update(dict(data))
            db.session.commit()
            return jsonify(post_schema.dump(post))
        except ValidationError as e:
            raise JsonValidationError(e)
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    
    def delete(self, post_id):
        post = Post.query.get(post_id)
        post.query.delete()
        db.session.commit()
        return jsonify({'response': 'ok!'}), 200


class CreatePostView(SwaggerView):

    tags = ['post']
    decorators = [
        token_required,
        permission_required(Post, one_of=['IsOwner', 'InPartners'])
    ]
    parameters = [
        {
            "in": "body",
            "name": "post",
            "type": "object",
            "schema": CreatePostSchema
        },
        {
            "in": "path",
            "name": "discussion_id",
            "type": "integer"
        }
    ]
    responses = {
        200: {
            "description": "Created post.",
            "schema": PostSchema
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
            post = create_post_schema.load(req_json)
            post.owner_id = g.user.id
            post.discussion_id = discussion_id
            db.session.add(post)
            db.session.commit()
            return jsonify(post_schema.dump(post))
        except ValidationError as e:
            raise JsonValidationError(e)
        except IntegrityError:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
