
from flask_marshmallow import Schema, fields
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import Nested

from discussion.app import ma
from discussion.models.discussion import Discussion
from discussion.models.user import User
from discussion.schemas.invitation import InvitationSchema
from discussion.schemas.post import PostSchema


class CreateDiscussionSchema(ma.Schema):
    title = ma.Str()
    description = ma.Str()


class EditDiscussionSchema(ma.Schema):
    title = ma.Str()
    description = ma.Str()


class DiscussionSchema(ma.Schema):
    id = ma.Integer()
    title = ma.Str()
    description = ma.Str()
    created_at = ma.DateTime()
    participants = ma.Nested('UserSchema', only=('id', 'username', 'email', 'first_name', ), many=True)
    followed_by = ma.Nested('UserSchema', only=('id', 'username', 'email', 'first_name', ), many=True)
    owner = Nested('UserSchema', only=('id', 'username', 'email', 'first_name', ))
    posts = Nested('PostSchema', only=('id', 'body'), many=True)
    invitations = Nested('InvitationSchema', only=('id', 'body', 'partner', 'status'), many=True)