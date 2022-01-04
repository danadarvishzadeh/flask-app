from discussion.app import ma
# from discussion.blueprints.discussions.schemas import discussion_schema
from discussion.models.post import Post
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
    
    body = auto_field(validate=[validate.Length(min=20, max=500)])


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
    author = Nested('UserSchema', exclude=('created_discussions',))
    parent_discussion = Nested('DiscussionSchema', exclude=('posts', 'creator'))


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
    author = Nested('SummerisedUserSchema')
    parent_discussion = Nested('SummerisedDiscussionSchema')


create_post_schema = CreatePostSchema()
post_schema = PostSchema()
summerised_post_schema = SummerisedPostSchema()