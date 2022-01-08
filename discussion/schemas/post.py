from flask_marshmallow import Schema, fields
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from discussion.app import ma
from discussion.models.post import Post


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
            'created_at',
            'owner',
            'parent_discussion',
        )
    owner = Nested('SummerisedUserSchema')
    parent_discussion = Nested('DiscussionSchema', exclude=('posts', 'owner'))


class SummerisedPostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        fields = (
            'id',
            'body',
            'date_created',
            'owner',
            'parent_discussion',
        )
    owner = Nested('SummerisedUserSchema')
    parent_discussion = Nested('SummerisedDiscussionSchema')


create_post_schema = CreatePostSchema()
post_schema = PostSchema()
summerised_post_schema = SummerisedPostSchema()
