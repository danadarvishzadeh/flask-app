import traceback

from discussion.app import db
from discussion.blueprints.posts import bp
from discussion.models.discussion import Discussion
from discussion.models.post import Post
from discussion.schemas.post import (CreatePostSchema, EditPostSchema,
                                     PostSchema)
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.utils.auth import token_required
from discussion.utils.errors import (InvalidAttemp, JsonIntegrityError,
                                     ResourceDoesNotExists)
from discussion.utils.permissions.decorators import permission_required
from flask import g, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

@bp.route('/<int:post_id>', methods=["GET", "PUT", "DELETE"])
class PostDetailView(MethodView):

    @bp.response(200, PostSchema)
    def get(self, post_id):
        post = Post.query.get(post_id)
        if post:
            return post
        logger.warning(f'Resource does not exists.')
        raise ResourceDoesNotExists()
    
    @token_required
    @permission_required(Post, required_permissions=["IsOwner"])
    @bp.arguments(EditPostSchema)
    @bp.response(204)
    def put(self, update_data, post_id):
        try:
            g.resource.update(update_data)
        except IntegrityError as e:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except AttributeError:
            logger.warning(f'Resource does not exists.')
            raise ResourceDoesNotExists()
        except:
            logger.exception('')
            raise InvalidAttemp()

    @token_required    
    @permission_required(Post, required_permissions=["IsOwner"])
    @bp.response(204)
    def delete(self, post_id):
        g.resource.delete()



@bp.route('/<int:discussion_id>', methods=["POST"])
class PostView(MethodView):

    @token_required
    @permission_required(Post, required_permissions=["IsOwner"])
    @bp.arguments(CreatePostSchema)
    @bp.response(200, PostSchema)
    def post(self, creation_data, discussion_id):
        try:
            creation_data.upadte({'discussion_id': discussion_id, 'owner_id': g.user.id})
            return Post(**creation_data).save()
        except IntegrityError:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            logger.exception('')
            raise InvalidAttemp()
