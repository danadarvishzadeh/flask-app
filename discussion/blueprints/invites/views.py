from sqlalchemy import or_, and_
from discussion.app import db
from discussion.blueprints.invites import bp
from discussion.models.discussion import Discussion
from discussion.models.invitation import Invitation
from discussion.schemas.invitation import (CreateInvitationSchema,
                                           InvitaionResponseSchema,
                                           InvitationSchema)
from discussion.utils.auth import token_required
from discussion.utils.errors import InvalidAttemp, JsonIntegrityError
from discussion.utils.permissions.decorators import permission_required
from flask import g
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

@bp.route('/<int:discussion_id>', methods=["GET", "POST", "PUT"])
class InvitationView(MethodView):

    @token_required()
    @permission_required(Discussion, store_resource=False, one_of=["IsOwner", "IsPartner"])
    @bp.response(200, InvitationSchema)
    def get(self, discussion_id):
        return Invitation.query.filter(
                    and_(Invitation.discussion_id==discussion_id,
                        or_(Invitation.partner_id==g.user.id,
                            Invitation.owner_id==g.user.id))).first()
        
    @token_required()
    @permission_required(Discussion, required_permissions=["IsOwner"])
    @bp.arguments(CreateInvitationSchema)
    @bp.response(200, InvitationSchema)
    def post(self, creation_data, discussion_id):
        try:
            creation_data.update({'discussion_id': discussion_id, 'owner_id': g.user.id})
            return Invitation(**creation_data).save()
        except IntegrityError as e:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            logger.exception('')
            raise InvalidAttemp()
    
    @token_required()
    @permission_required(Discussion, required_permissions=["IsInvited"])
    @bp.arguments(InvitaionResponseSchema)
    @bp.response(204)
    def put(self, response_data, discussion_id):
        try:
            Invitation.query.filter_by(discussion_id=discussion_id, partner_id=g.user.id).first().update(response_data)
        except IntegrityError as e:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            logger.exception('')
            raise InvalidAttemp()
