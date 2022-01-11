from flask_marshmallow import Schema, fields
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import *

from discussion.models.post import Post


class CreatePostSchema(Schema):
    body = Str(validate=[validate.Length(min=20, max=500)])


class PostSchema(Schema):
    id = Integer()
    body = Str()
    created_at = DateTime()
    owner = Nested('UserSchema', only=('id', 'username', 'email'))
    parent_discussion = Nested('DiscussionSchema', only=('id', 'title'))

class EditPostSchema(Schema):
    body = Str(validate=[validate.Length(min=20, max=500)])


create_post_schema = CreatePostSchema()
post_schema = PostSchema()
