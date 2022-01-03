import traceback
from discussion.app import db
from discussion.blueprints.invite import bp, logger
from discussion.blueprints.invite.schemas import invitation_schema, summerised_invitation_schema
from discussion.utils import paginate_invitations
from discussion.blueprints.users.views import token_required
from discussion.models import (Discussion, Follow, Invitation, Participate,
                               Post, User)
from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError



@bp.route('/discussions/<int:discussion_id>/invite/<int:user_id>/', methods=_post)
@token_required
@is_creator
def create_invitations(discussion_id, user_id):
    req_json = request.get_json()
    discussion = Discussion.query.get(discussion_id)
    try:
        invitation = create_invitation_schema.load(req_json)
        invitation.inviter_id = g.user.id
        invitation.invited_id = user_id
        invitation.discussion_id = discussion_id
        invitation.status = 'Sent'
        db.session.add(invitation)
        db.session.commit()
        return jsonify(summerised_invitation_schema.dump(invitation))
    except ValidationError as e:
        raise JsonValidationError(e)
    except IntegrityError:
        db.session.rollback()
        raise JsonIntegrityError()
    except:
        trace_info = traceback.format_exc()
        logger.error(f"uncaught exception: {trace_info}")
        raise InvalidAttemp()

@bp.route('/invitations/', methods=get)
@token_required
def get_invitations():
    page = request.args.get('page')
    print(g.user.id)
    print(g.user.username)
    data_set = db.session.query(Invitation).filter(or_(Invitation.invited_id==g.user.id, Invitation.inviter_id==g.user.id))
    return paginate_invitatinos(page, data_set, 'get_invitations')

@bp.route('/invitations/<int:invitation_id>/', methods=['PUT'])
@token_required
@is_invited
def edit_invitation_details(invitation_id):
    invitation = Invitation.query.get(invitation_id)
    if invitation.status == 'Sent':
        status = request.get_json().get('status')
        if status == 'Accepted':
            invitation.query.update({'status':status})
            participate = Participate()
            participate.host_id = invitation.inviter_id
            participate.participant_id = invitation.invited_id
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

@bp.route('/invitations/<int:invitation_id>/', methods=['DELETE'])
@token_required
@is_inviter_or_invited
def delete_invitation(invitation_id):
    if g.user == invitation.invited or g.user == invitation.inviter:
        invitation.query.delete()
        db.session.commit()
        return jsonify({'response': 'Ok!'}), 200
    else:
        logger.warning(f"{g.user.username} attempted to edit user {invitation.invited.username}'s invitation.")
        raise JsonPermissionDenied()
