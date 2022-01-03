from discussion.app import ma
from discussion.models import Post
from flask_marshmallow import Schema, fields
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field




class CreatePostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        fields = (
            'body',
        )
        load_instance = True


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        fields = (
            'id',
            'body',
            'date_created',
            'author',
            'parent_discussion',
        )
    author = Nested(lambda: UserSchema(exclude=('created_discussions',)))
    parent_discussion = Nested(lambda: DiscussionSchema(exclude=('posts', 'creator')))


class SummerisedPostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        fields = (
            'id',
            'body',
            'date_created',
            'author',
            'parent_discussion',
        )
    author = Nested(lambda: SummerisedUserSchema())
    parent_discussion = Nested(lambda: SummerisedDiscussionSchema())