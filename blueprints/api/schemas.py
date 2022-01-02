
from discussion.app import ma
from discussion.models import (Discussion, Follow, Invitation, Participate,
                               Post, User)
from flask_marshmallow import Schema, fields
from flask_marshmallow.sqla import HyperlinkRelated
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field


class CreateUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

    password = ma.String(required=True, validate=[validate.Length(min=8, max=24)])
    email = ma.String(required=True, validate=[validate.Email()])

    def __init__(self):
        super().__init__()
        self.fields.pop('password_hash')
    
    @post_load
    def lower_case(self, data, **kwargs):
        data['username'] = data['username'].lower()
        data['name'] = data['name'].lower()
        data['lastname'] = data['lastname'].lower()
        return data


class EditUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = (
            'name',
            'lastname',
        )


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
    created_discussions = Nested(lambda: DiscussionSchema(only=("id", "title", "description", 'participants', 'followed_by'), many=True))
    invitations_sent = Nested('SummerisedInvitationSchema', many=True)
    invitations_recived = Nested('SummerisedInvitationSchema', many=True)

    # participated = ma.Nested(lambda: UserSchema(only=('id', 'username', 'name', 'lastname', 'email'), many=True))
    # participated_with = ma.Nested(lambda: UserSchema(only=('id', 'username', 'name', 'lastname', 'email'), many=True))

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

    creator = Nested(SummerisedUserSchema)
    posts = Nested(lambda: SummerisedPostSchema(), many=True)
    invitations = Nested(lambda: InvitationSchema(only=('id', 'body', 'invited', 'status'), many=True))

    @post_dump()
    def load_participants(self, data, **kwargs):
        discussion = Discussion.query.get(data['id'])
        participants = summerised_user_schema.dump(discussion.get_participants(), many=True)
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

    invited = Nested(SummerisedUserSchema)
    inviter = Nested(SummerisedUserSchema)
    discussion = Nested(lambda: SummerisedDiscussionSchema())


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
edit_user_schema = EditUserSchema()
summerised_invitation_schema = SummerisedInvitationSchema()
summerised_post_schema = SummerisedPostSchema()
