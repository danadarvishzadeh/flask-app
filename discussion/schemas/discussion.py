
from flask_marshmallow import Schema
from marshmallow.fields import Nested, Str, DateTime, Integer


class BaseDiscussionSchema(Schema):
    title = Str()
    description = Str()


class CreateDiscussionSchema(BaseDiscussionSchema):
    pass


class EditDiscussionSchema(BaseDiscussionSchema):
    pass


class DiscussionSchema(BaseDiscussionSchema):
    id = Integer()
    created_at = DateTime()
    participants = Nested('UserSchema', only=('id', 'username', 'email', 'first_name', ), many=True)
    followed_by = Nested('UserSchema', only=('id', 'username', 'email', 'first_name', ), many=True)
    owner = Nested('UserSchema', only=('id', 'username', 'email', 'first_name', ))
    posts = Nested('PostSchema', only=('id', 'body'), many=True)
    invitations = Nested('InvitationSchema', only=('id', 'body', 'partner', 'status'), many=True)