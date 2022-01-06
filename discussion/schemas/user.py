
from flask_marshmallow import Schema, fields
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from werkzeug.security import generate_password_hash

from discussion.app import ma
from discussion.models.follow import Follow
from discussion.models.participate import Participate
from discussion.models.user import User



class CreateUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

    password = ma.String(required=True, validate=[validate.Length(min=8, max=24)])
    email = ma.String(required=True, validate=[validate.Email()])
    

    @post_load
    def lower_case(self, data, **kwargs):
        data['username'] = data['username'].lower()
        data['name'] = data['name'].lower()
        data['lastname'] = data['lastname'].lower()
        data['password'] = generate_password_hash(data['password'])
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

    created_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    invitations_sent = Nested('InvitationSchema', many=True)
    invitations_recived = Nested('InvitationSchema', many=True)

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
        participated_in = [summerised_user_schema.dump(p.participant) for p in User.query.get(data['id']).participated_with_users]
        data['participated_with_users'] = participated_in
        return data
    
    @post_dump()
    def load_host_of(self, data, **kwargs):
        host_of = [summerised_user_schema.dump(p.host) for p in User.query.get(data['id']).host_for]
        data['host_for'] = host_of
        return data

create_user_schema = CreateUserSchema()
edit_user_schema = EditUserSchema()
user_schema = UserSchema()
summerised_user_schema = SummerisedUserSchema()
