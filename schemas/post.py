from flask_marshmallow import Schema
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import Nested, DateTime, Integer, Str


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