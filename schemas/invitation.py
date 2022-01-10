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

    partner = Nested('UserSchema', only=('id', 'username', 'email'))
    owner = Nested('UserSchema', only=('id', 'username', 'email', 'created_discussions'))
    discussion = Nested('DiscussionSchema', only=('id', 'title'))


class ParticipateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Participate
        fields = (
            'id',
            'date_started',
            'partner',
            'owner',
            'discussion',
        )
    
    owned_participations = Nested('UserSchema', only=('id', 'username', 'email'))
    partnered_participations = Nested('UserSchema', only=('id', 'username', 'email'))
    discussion = Nested('DiscussionSchema', only=('id', 'title'))

invitation_schema = InvitationSchema()
create_invitation_schema = CreateInvitationSchema()
