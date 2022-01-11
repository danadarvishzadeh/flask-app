from flask_marshmallow import Schema, fields
from marshmallow.fields import Nested, DateTime, Integer, Str

# from discussion.app.ma import Schema
from discussion.models.invitation import Invitation
from discussion.models.participate import Participate


class CreateInvitationSchema(Schema):
    partner_id = Integer()
    body = Str()


class InvitationSchema(Schema):

    id = Integer()
    partner = Nested('UserSchema', only=('id', 'username', 'email'))
    owner = Nested('UserSchema', only=('id', 'username', 'email'))
    discussion = Nested('DiscussionSchema', only=('id', 'title'))
    body = Str()
    status = Str()


class InvitaionResponseSchema(Schema):
    response = Str()

class ParticipateSchema(Schema):
    id = Integer()
    created_at = DateTime()
    owner = Nested('UserSchema', only=('id', 'username', 'email'))
    discussion = Nested('DiscussionSchema', only=('id', 'title'))
    partner = Nested('UserSchema', only=('id', 'username', 'email'))
    owned_participations = Nested('UserSchema', only=('id', 'username', 'email'))
    partnered_participations = Nested('UserSchema', only=('id', 'username', 'email'))
