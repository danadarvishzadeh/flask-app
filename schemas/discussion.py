
from flask_marshmallow import Schema, fields
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from discussion.app import ma
from discussion.models.discussion import Discussion
from discussion.models.user import User
from discussion.schemas.invitation import InvitationSchema
from discussion.schemas.user import user_schema
from flasgger import Schema, fields



class CreateDiscussionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Discussion
        fields = (
            'title',
            'description',
        )
        load_instance = True


class DiscussionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Discussion
        fields = (
            'id',
            'title',
            'description',
            'created_at',
            'owner',
            'posts',
            'invitations',
            'participants',
            'followed_by',
        )

    owner = Nested('UserSchema', only=('id', 'username', 'email', 'name', ))
    posts = Nested('PostSchema', only=('id', 'body'), many=True)
    invitations = Nested('InvitationSchema', only=('id', 'body', 'partner', 'status'), many=True)

discussion_schema = DiscussionSchema()
create_discussion_schema = CreateDiscussionSchema()