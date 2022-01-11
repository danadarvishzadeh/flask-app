import traceback

from discussion.app import db
from discussion.blueprints.posts import bp, logger
from discussion.models.discussion import Discussion
from discussion.models.post import Post
from discussion.schemas.post import (CreatePostSchema, EditPostSchema,
                                     PostSchema, create_post_schema,
                                     post_schema)
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.utils.auth import token_required
from discussion.utils.errors import (InvalidAttemp, JsonIntegrityError,
                                     ResourceDoesNotExists)
from discussion.utils.permissions.decorators import permission_required
from flask import g, jsonify, request
from flask.views import MethodView
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError


@bp.route('/<int:post_id>', methods=["GET", "PUT", "DELETE"])
class PostDetailView(MethodView):

    def get(self, post_id):
        post = Post.query.get(post_id)
        if post:
            return jsonify(post_schema.dump(post))
        logger.warning(f"Trying to access non-existing post with id {post_id}")
        raise ResourceDoesNotExists()
    
    @token_required
    @permission_required(Post, required_permissions=["IsOwner"])
    @bp.arguments(EditPostSchema)
    def put(self, update_data, post_id):
        try:
            g.resource.update(update_data)
        except IntegrityError as e:
            db.session.rollback()
            raise JsonIntegrityError()
        except AttributeError:
            raise ResourceDoesNotExists()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()

    @token_required    
    @permission_required(Post, required_permissions=["IsOwner"])
    def delete(self, post_id):
        g.resource.delete()



@bp.route('/<int:discussion_id>', methods=["POST"])
class PostView(MethodView):

    @token_required
    @permission_required(Post, required_permissions=["IsOwner"])
    @bp.arguments(CreatePostSchema)
    def post(self, creation_data, discussion_id):
        try:
            creation_data.upadte({'discussion_id': discussion_id, 'owner_id': g.user.id})
            return jsonify(post_schema.dump(Post(**creation_data).save()))
        except IntegrityError:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
