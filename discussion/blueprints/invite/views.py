import traceback
from discussion.app import db
from discussion.blueprints.invite import bp, logger
from discussion.schemas.invitation import create_invitation_schema, invitation_schema
from discussion.models.invitation import Invitation
from discussion.models.discussion import Discussion
from discussion.models.participate import Participate
from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from discussion.utils.perms.decorators import permission_required
from discussion.utils.auth import token_required 
from discussion.utils.errors import (InvalidAttemp, JsonIntegrityError,
                               JsonValidationError, ResourceDoesNotExists, ActionIsNotPossible)
from marshmallow.exceptions import ValidationError
from discussion.blueprints.invite.paginators import InvitationPaginator


@bp.route('/<int:discussion_id>/<int:user_id>/', methods=['POST'])
@token_required
@permission_required(Discussion, required=['IsOwner'])
def create_invitations(discussion_id, user_id):
    req_json = request.get_json()
    discussion = Discussion.query.get(discussion_id)
    try:
        invitation = create_invitation_schema.load(req_json)
        invitation.owner_id = g.user.id
        invitation.partner_id = user_id
        invitation.discussion_id = discussion_id
        invitation.status = 'Sent'
        db.session.add(invitation)
        db.session.commit()
        return jsonify(invitation_schema.dump(invitation))
    except ValidationError as e:
        print(e)
        raise JsonValidationError(e)
    except IntegrityError:
        db.session.rollback()
        raise JsonIntegrityError()
    except:
        trace_info = traceback.format_exc()
        logger.error(f"uncaught exception: {trace_info}")
        raise InvalidAttemp()

@bp.route('/', methods=['GET'])
@token_required
def get_invitations():
    page = request.args.get('page')
    return InvitationPaginator.return_page(page, 'get_invitations')

@bp.route('/<int:invitation_id>/', methods=['PUT'])
@token_required
@permission_required(Invitation ,one_of=['IsPartner'])
def edit_invitation_details(invitation_id):
    invitation = Invitation.query.get(invitation_id)
    if invitation.status == 'Sent':
        status = request.get_json().get('status')
        if status == 'Accepted':
            invitation.query.update({'status':status})
            participate = Participate()
            participate.owner_id = invitation.owner_id
            participate.partner_id = invitation.partner_id
            participate.discussion_id = invitation.discussion_id
            db.session.add(participate)
        elif status == 'Rejected':
            invitation.query.update({'status':status})
        else:
            raise JsonValidationError('Provide a valid answer. ["Accepted", "Rejected"]')
        try:
            db.session.commit()
            return jsonify({'response': 'Ok!'}), 200
        except IntegrityError:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    else:
        raise ActionIsNotPossible('The action that you requested can not be done.')

@bp.route('/<int:invitation_id>/', methods=['DELETE'])
@token_required
@permission_required(Invitation, one_of=['IsOwner', 'IsPartner'])
def delete_invitation(invitation_id):
    invitation = Invitation.query.filter_by(id=invitation_id).delete()
    db.session.commit()
    return jsonify({'response': 'Ok!'}), 200