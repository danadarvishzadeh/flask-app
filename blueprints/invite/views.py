import traceback
from discussion.app import db
from discussion.blueprints.invite import bp, logger
from discussion.schemas.invitation import create_invitation_schema, invitation_schema, InvitationSchema, CreateInvitationSchema
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
from flasgger import SwaggerView
from discussion.schemas.response import ErrorSchema, OkResponse


class InvitationView(SwaggerView):
    parameters = [
        {
            "in": "path",
            "name": "discussion_id",
            "type": "string"
        }
    ]
    responses = {
        200: {
            "description": "invitation detail.",
            "schema": InvitationSchema
        },
        400: {
            "description": "not found.",
            "schema": ErrorSchema
        }
    }
    def get(self, discussion_id):
        page = request.args.get('page')
        return InvitationPaginator.return_page(page, 'get_invitations')


class CreateInvitationView(SwaggerView):

    decorators = [
        token_required,
        permission_required(Discussion, required_permissions=['IsOwner'])
    ]
    parameters = [
        {
            "in": "body",
            "name": "invitation",
            "type": "object",
            "schema": CreateInvitationSchema
        },
        {
            "in": "path",
            "name": "user_id",
            "type": "string",
        },
        {
            "in": "path",
            "name": "discussion_id",
            "type": "string",
        },
    ]
    validate = True
    responses = {
        200: {
            "description": "invitation created.",
            "schema": InvitationSchema
        },
        400: {
            "description": "not found.",
            "schema": ErrorSchema
        }
    }

    def post(self, discussion_id, user_id):
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
            raise JsonValidationError(e)
        except IntegrityError:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    
class ChangeInvitationView(SwaggerView):
    decorators = [
        token_required,
        permission_required(Invitation ,one_of=['IsPartner'])
    ]
    parameters = [
        {
            "in": "path",
            "name": "invitation_id",
            "type": "string"
        },
        {
            "in": "body",
            "name": "response",
            "type": "string"
        }
    ]
    responses = {
        200: {
            "description": "response submited.",
            "schema": OkResponse
        },
        400: {
            "description": "not found.",
            "schema": ErrorSchema
        }
    }

    def put(self, invitation_id):
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


class DeleteInvitationView(SwaggerView):
    decorators = [
        token_required,
        permission_required(Invitation , one_of=['IsOwner', 'IsPartner'])
    ]
    parameters = [
        {
            "in": "path",
            "name": "invitation_id",
            "type": "string"
        },
    ]
    responses = {
        200: {
            "description": "invitation deleted.",
            "schema": OkResponse
        },
        400: {
            "description": "not found.",
            "schema": ErrorSchema
        }
    }


    def delete(self, invitation_id):
        invitation = Invitation.query.filter_by(id=invitation_id).delete()
        db.session.commit()
        return jsonify({'response': 'Ok!'}), 200