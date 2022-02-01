from discussion.app import db
from discussion.blueprints.posts import bp
from discussion.models.discussion import Discussion
from discussion.models.post import Post
from discussion.schemas import PaginationSchema
from discussion.schemas.post import (CreatePostSchema, EditPostSchema,
                                     PostSchema)
from discussion.utils.auth import token_required
from discussion.utils.errors import (InvalidAttemp, JsonIntegrityError,
                                     ResourceDoesNotExists)
from discussion.utils.paginators.post import PostPaginator
from discussion.utils.permissions.decorators import permission_required
from flask import g
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
import logging
from discussion.extentions import cache


logger = logging.getLogger(__name__)


@bp.route('/<int:discussion_id>', methods=["POST"])
class PostView(MethodView):


    @bp.arguments(PaginationSchema, location="query")
    @bp.response(200, PostSchema(many=True))
    def get(self, pagination_parameters):
        # posts = Post.query.all()
        # pagination_parameters.item_count = len(posts)
        # return posts[
        #     pagination_parameters.first_item:pagination_parameters.last_item+1
        # ]
        page = pagination_parameters.get('page')
        if not page:
            page = 1
        return PostPaginator().return_page(page, 'posts.PostView')

    @token_required()
    @permission_required(Discussion, required_permissions=["IsOwner"])
    @bp.arguments(CreatePostSchema)
    @bp.response(200, PostSchema)
    def post(self, creation_data, discussion_id):
        try:
            creation_data.update({'discussion_id': discussion_id, 'owner_id': g.user.id})
            return Post(**creation_data).save()
        except IntegrityError as e:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            logger.exception('')
            raise InvalidAttemp()


@bp.route('/<int:post_id>', methods=["GET", "PUT", "DELETE"])
class PostDetailView(MethodView):

    @cache.cached(timeout=50)
    @bp.response(200, PostSchema)
    def get(self, post_id):
        post = Post.query.get(post_id)
        if post:
            return post
        logger.warning(f'Resource does not exists.')
        raise ResourceDoesNotExists()
    
    @token_required()
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

    @token_required()    
    @permission_required(Post, required_permissions=["IsOwner"])
    @bp.response(204)
    def delete(self, post_id):
        g.resource.delete()