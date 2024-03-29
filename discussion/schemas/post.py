from flask_marshmallow import Schema
from marshmallow import validate
from marshmallow.fields import Nested, DateTime, Integer, Str


class BasePostSchema(Schema):
    body = Str(validate=[validate.Length(min=20, max=500)])


class CreatePostSchema(BasePostSchema):
    pass


class EditPostSchema(BasePostSchema):
    pass


class PostSchema(BasePostSchema):
    id = Integer()
    body = Str()
    created_at = DateTime()
    owner = Nested('UserSchema', only=('id', 'username', 'email'))
    parent_discussion = Nested('DiscussionSchema', only=('id', 'title'))