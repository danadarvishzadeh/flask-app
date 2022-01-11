import traceback

from discussion.app import db
from discussion.blueprints.invites import bp, logger
from discussion.models.discussion import Discussion
from discussion.models.invitation import Invitation
from discussion.schemas.invitation import (CreateInvitationSchema,
                                           InvitaionResponseSchema,
                                           InvitationSchema)
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.utils.auth import token_required
from discussion.utils.errors import (InvalidAttemp, JsonIntegrityError,
                                     ResourceDoesNotExists)
from discussion.utils.permissions.decorators import permission_required
from flask import g, jsonify
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError


@bp.route('/<int:discussion_id>', methods=["GET", "POST", "PUT"])
class InvitationView(MethodView):


    def get(self, discussion_id):
        page = request.args.get('page')
        return InvitationPaginator.return_page(page, 'get_invitations')
        
    @token_required
    @permission_required(Discussion, required_permissions=["IsOwner"])
    @bp.arguments(CreateInvitationSchema)
    def post(self, creation_data, discussion_id):
        try:
            creation_data.update({'discussion_id': discussion_id, 'owner_id': g.user.id})
            return jsonify(InvitationSchema().dump(Invitation(**creation_data).save()))
        except IntegrityError:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    
    @token_required
    @permission_required(Discussion, required_permissions=["IsInvited"])
    @bp.arguments(InvitaionResponseSchema)
    def put(self, response_data, discussion_id):
        try:
            Invitation.query.filter('discussion_id'==discussion_id, 'partner_id'==g.user.id).update(response_data)
        except IntegrityError:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
