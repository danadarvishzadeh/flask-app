
from discussion.app import ma
from flask_marshmallow import Schema, fields
from marshmallow.fields import Nested
# from marshmallow import post_load, ValidationError, validates, validate, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from flask_marshmallow.sqla import HyperlinkRelated
from discussion.models import (User, Discussion,
                                Post, Invitation,
                                Participate,)
# from flask_marshmallow.fields import URLFor
from marshmallow.decorators import post_dump


class CreateUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

    password = ma.String(required=True)

    def __init__(self):
        super().__init__()
        self.fields.pop('password_hash')


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'name',
            'lastname',
            'created_discussions',
            'participated_discussions',
            'participated',
            'participated_with',
            'followed_discussions',
            'invitations_sent',
            'invitations_recived',
        )

    id = auto_field(dump_only=True)
    username = auto_field(dump_only=True)
    email = auto_field(dump_only=True)
    created_discussions = Nested(lambda: DiscussionSchema(only=("id", "title", "description"), many=True), dump_only=True)
    invitations_sent = Nested(lambda: InvitationSchema(only=('id', 'body', 'inviter', 'status'), many=True), dump_only=True)
    invitations_recived = Nested(lambda: InvitationSchema(only=('id', 'body', 'inviter', 'status'), many=True), dump_only=True)

    # participated_discussions = Nested(lambda: DiscussionSchema(only=('id', 'title', 'description'), many=True), dump_only=True)
    # followed_discussions = Nested(lambda: DiscussionSchema(only=('id', 'title', 'description'), many=True), dump_only=True)
    participated = ma.Nested(lambda: UserSchema(only=('id', 'username', 'name', 'lastname', 'email'), many=True), dump_only=True)
    participated_with = ma.Nested(lambda: UserSchema(only=('id', 'username', 'name', 'lastname', 'email'), many=True), dump_only=True)



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
            'date_created',
            'creator',
            'posts',
            'invitations',
            'participants',
            'followed_by',
        )

    id = auto_field(dump_only=True)
    date_created = auto_field(dump_only=True)
    creator = Nested(lambda: UserSchema(only=('id', 'username', 'name', 'lastname', 'email')), dump_only=True)
    posts = Nested(lambda: PostSchema(only=('id', 'body', 'date_created'), many=True), dump_only=True)
    invitations = Nested(lambda: InvitationSchema(only=('id', 'body', 'invited', 'status'), many=True), dump_only=True)


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
    id = auto_field(dump_only=True)
    date_created = auto_field(dump_only=True)
    author = Nested(lambda: UserSchema(exclude=('created_discussions',)), dump_only=True)
    parent_discussion = Nested(lambda: DiscussionSchema(exclude=('posts', 'author')), dump_only=True)


class CreatePostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        fields = (
            'body',
        )
        load_instance = True


class CreateInvitationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Invitation
        load_instance = True
        fields = (
            'id',
            'body',
            'date_sent',
        )


class InvitationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Invitation
        fields = (
            'id',
            'body',
            'date_sent',
            'invited',
            'inviter',
            'status',
            'discussion',
        )

    invited = Nested(lambda: UserSchema(only=(
        'id', 'name', 'lastname', 'username', 'email')), dump_only=True)
    inviter = Nested(lambda: UserSchema(only=(
        'id', 'name', 'lastname', 'username', 'email')), dump_only=True)
    discussion = Nested(lambda: DiscussionSchema(only=(
        'id', 'title', 'description', 'date_created')), dump_only=True)


class ParticipateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Participate
        fields = (
            'id',
            'date_started',
            'paricipated_with',
            'participated',
            'discussion',
        )
    
    paricipated_with = Nested(lambda: UserSchema(only=(
        'id', 'name', 'lastname', 'username', 'email')), dump_only=True)
    participated = Nested(lambda: UserSchema(only=(
        'id', 'name', 'lastname', 'username', 'email')), dump_only=True)
    discussion = Nested(lambda: DiscussionSchema(only=(
        'id', 'title', 'description', 'date_created')), dump_only=True)


class ParticipateDiscussionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Participate
        fields = (
            'participated',
        )
        participated = Nested(lambda: UserSchema(only=(
        'id', 'name', 'lastname', 'username', 'email')), dump_only=True)


create_user_schema = CreateUserSchema()
user_schema = UserSchema()
discussion_schema = DiscussionSchema()
create_discussion_schema = CreateDiscussionSchema()
post_schema = PostSchema()
create_post_schema = CreatePostSchema()
create_invitation_schema = CreateInvitationSchema()
invitation_schema = InvitationSchema()