from flask_marshmallow import Schema, fields
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from discussion.app import ma
from discussion.models.invitation import Invitation
from discussion.models.participate import Participate


class CreateInvitationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Invitation
        load_instance = True
        fields = (
            'id',
            'body',
            'date_sent',
        )


class InvitationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Invitation
        fields = (
            'id',
            'body',
            'created_at',
            'partner',
            'owner',
            'status',
            'discussion',
        )

    partner = Nested('SummerisedUserSchema')
    owner = Nested('SummerisedUserSchema')
    discussion = Nested('SummerisedDiscussionSchema')


class ParticipateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Participate
        fields = (
            'id',
            'date_started',
            'owned_participations',
            'partnered_participations',
            'discussion',
        )
    
    owned_participations = Nested('SummerisedUserSchema')
    partnered_participations = Nested('SummerisedUserSchema')
    discussion = Nested('DiscussionSchema')

invitation_schema = InvitationSchema()
create_invitation_schema = CreateInvitationSchema()
