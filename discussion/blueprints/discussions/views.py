
from discussion.app import db
from discussion.blueprints.discussions import bp
from discussion.models.discussion import Discussion
from discussion.schemas.discussion import CreateDiscussionSchema, DiscussionSchema, EditDiscussionSchema, PaginationSchema
from discussion.utils.auth import token_required
from discussion.utils.errors import InvalidAttemp, JsonIntegrityError, ResourceDoesNotExists
from discussion.utils.permissions.decorators import permission_required
from flask.views import MethodView
from flask import g
from sqlalchemy.exc import IntegrityError
from logging import getLogger
from discussion.extentions import cache

logger = getLogger(__name__)


@bp.route('/', methods=['POST', 'GET'])
class DiscussionView(MethodView):

    @bp.arguments(PaginationSchema, location="query")
    @bp.response(200, DiscussionSchema(many=True))
    def get(self, pagination_parameters):
        discussions = Discussion.query.all()
        pagination_parameters.item_count = len(discussions)
        return discussions[
            pagination_parameters.first_item:pagination_parameters.last_item+1
        ]

    @token_required()
    @bp.arguments(CreateDiscussionSchema)
    @bp.response(200, DiscussionSchema)
    def post(self, creation_data):
        try:
            creation_data.update({'owner_id': g.user.id})
            return Discussion(**creation_data).save()
        except IntegrityError as e:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except Exception as e:
            logger.exception('')
            raise InvalidAttemp()


@bp.route('/<int:discussion_id>', methods=['GET', 'PUT', 'DELETE'])
class DiscussionDetailView(MethodView):

    @cache.cached(timeout=50)
    @bp.response(200, DiscussionSchema)
    def get(self, discussion_id):
        discussion = Discussion.query.get(discussion_id)
        if discussion:
            return discussion
        logger.warning(f'Resource does not exists.')
        raise ResourceDoesNotExists()

    @token_required()
    @permission_required(Discussion, required_permissions=["IsOwner"])
    @bp.arguments(EditDiscussionSchema)
    @bp.response(204)
    def put(self, update_data, discussion_id):
        try:
            g.resource.update(update_data)
        except IntegrityError as e:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except Exception as e:
            logger.exception('')
            raise InvalidAttemp()
    
    @token_required()
    @permission_required(Discussion, required_permissions=["IsOwner"])
    @bp.response(204)
    def delete(self, discussion_id):
        g.resource.delete()