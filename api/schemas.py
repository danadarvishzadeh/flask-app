
from discussion.app import ma
from flask_marshmallow import Schema, fields
from marshmallow.fields import Nested
# from marshmallow import post_load, ValidationError, validates, validate, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from flask_marshmallow.sqla import HyperlinkRelated
from discussion.models import (User, Discussion,
                                Post, Invitation,
                                Participate, Follow )
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


class SummerisedUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'name',
            'lastname',
        )

class SummerisedDiscussionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Discussion
        fields = (
            'id',
            'title',
            'body',
        )

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
            'invitations_sent',
            'invitations_recived',
        )

    id = auto_field(dump_only=True)
    username = auto_field(dump_only=True)
    email = auto_field(dump_only=True)
    created_discussions = Nested(lambda: DiscussionSchema(only=("id", "title", "description", 'participants', 'followed_by'), many=True), dump_only=True)
    invitations_sent = Nested('SummerisedInvitationSchema', many=True)
    invitations_recived = Nested('SummerisedInvitationSchema', many=True)

    # participated = ma.Nested(lambda: UserSchema(only=('id', 'username', 'name', 'lastname', 'email'), many=True), dump_only=True)
    # participated_with = ma.Nested(lambda: UserSchema(only=('id', 'username', 'name', 'lastname', 'email'), many=True), dump_only=True)

    @post_dump()
    def load_followed_discussions(self, data, **kwargs):
        followed_discussions = [summerised_discussion_schema.dump(f.discussion) for f in Follow.query.filter_by(follower_id=data['id'])]
        data['followed_discussions'] = followed_discussions
        return data
    
    @post_dump()
    def load_participated_discussions(self, data, **kwargs):
        participated_discussions = [summerised_discussion_schema.dump(p.discussion) for p in Participate.query.filter_by(participant_id=data['id'])]
        data['participated_discussions'] = participated_discussions
        return data
    
    @post_dump()
    def load_participated_in(self, data, **kwargs):
        # print(User.query.get(data['id']).participated[0].participated)
        participated_in = [summerised_user_schema.dump(p.participant) for p in User.query.get(data['id']).participated_with_users]
        data['participated_with_users'] = participated_in
        return data
    
    @post_dump()
    def load_host_of(self, data, **kwargs):
        # print(User.query.get(data['id']).participated[0].participated)
        host_of = [summerised_user_schema.dump(p.host) for p in User.query.get(data['id']).host_for]
        data['host_for'] = host_of
        return data


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
    creator = Nested(SummerisedUserSchema)
    posts = Nested(lambda: PostSchema(only=('id', 'body', 'date_created'), many=True))
    invitations = Nested(lambda: InvitationSchema(only=('id', 'body', 'invited', 'status'), many=True))

    @post_dump()
    def load_participants(self, data, **kwargs):
        participants = [summerised_user_schema.dump(User.query.get(p.participant_id)) for p in data['participants']]
        data['participants'] = participants
        return data
    
    @post_dump()
    def load_followed_by(self, data, **kwargs):
        followed_by = [summerised_user_schema.dump(User.query.get(f.follower_id)) for f in data['followed_by']]
        data['followed_by'] = followed_by
        return data


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

    invited = Nested(SummerisedUserSchema, dump_only=True)
    inviter = Nested(SummerisedUserSchema, dump_only=True)
    discussion = Nested(lambda: DiscussionSchema(only=(
        'id', 'title', 'description', 'date_created', 'participants')), dump_only=True)


class SummerisedInvitationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Invitation
        fields = (
            'id',
            'body',
            'date_sent',
            'status',
        )

    invited = Nested(SummerisedUserSchema)
    inviter = Nested(SummerisedUserSchema)
    discussion = Nested(SummerisedDiscussionSchema)

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
    
    paricipated_with = Nested(SummerisedUserSchema)
    participated = Nested(SummerisedUserSchema)
    discussion = Nested(DiscussionSchema)


create_user_schema = CreateUserSchema()
user_schema = UserSchema()
discussion_schema = DiscussionSchema()
create_discussion_schema = CreateDiscussionSchema()
post_schema = PostSchema()
create_post_schema = CreatePostSchema()
create_invitation_schema = CreateInvitationSchema()
invitation_schema = InvitationSchema()
summerised_user_schema = SummerisedUserSchema()
summerised_discussion_schema = SummerisedDiscussionSchema()