
from flask_marshmallow import Schema
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import Nested, Str, DateTime, Integer



class CreateDiscussionSchema(Schema):
    title = Str()
    description = Str()


class EditDiscussionSchema(Schema):
    title = Str()
    description = Str()


class DiscussionSchema(Schema):
    id = Integer()
    title = Str()
    description = Str()
    created_at = DateTime()
    participants = Nested('UserSchema', only=('id', 'username', 'email', 'first_name', ), many=True)
    followed_by = Nested('UserSchema', only=('id', 'username', 'email', 'first_name', ), many=True)
    owner = Nested('UserSchema', only=('id', 'username', 'email', 'first_name', ))
    posts = Nested('PostSchema', only=('id', 'body'), many=True)
    invitations = Nested('InvitationSchema', only=('id', 'body', 'partner', 'status'), many=True)