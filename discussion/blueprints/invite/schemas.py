from discussion.app import ma
from discussion.models import Invitation
from flask_marshmallow import Schema, fields
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field





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
            'date_sent',
            'invited',
            'inviter',
            'status',
            'discussion',
        )

    invited = Nested('SummerisedUserSchema')
    inviter = Nested('SummerisedUserSchema')
    discussion = Nested(lambda: SummerisedDiscussionSchema())


class SummerisedInvitationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Invitation
        fields = (
            'id',
            'body',
            'date_sent',
            'status',
        )

    invited = Nested('SummerisedUserSchema')
    inviter = Nested('SummerisedUserSchema')
    discussion = Nested('SummerisedDiscussionSchema')

class ParticipateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Participate
        fields = (
            'id',
            'date_started',
            'paricipated_with',
            'participated',
            'discussion',
        )
    
    paricipated_with = Nested('SummerisedUserSchema')
    participated = Nested('SummerisedUserSchema')
    discussion = Nested('DiscussionSchema')