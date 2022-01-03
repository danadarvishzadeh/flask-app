
from discussion.app import ma
from discussion.models.discussion import Discussion
from discussion.models.user import User
from flask_marshmallow import Schema, fields
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field


class SummerisedDiscussionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Discussion
        fields = (
            'id',
            'title',
            'body',
        )


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

    creator = Nested('SummerisedUserSchema')
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

create_discussion_schema = CreateDiscussionSchema()
discussion_schema = DiscussionSchema()