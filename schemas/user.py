
from flask_marshmallow import Schema, fields
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load, pre_load
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
        fields = (
            'username',
            'name',
            'lastname',
            'password',
            'email',
        )
    password = ma.String(required=True, validate=[validate.Length(min=8, max=24)])
    email = ma.String(required=True, validate=[validate.Email()])
    

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


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'name',
            'lastname',
        )

    participated_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    hosted_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    owned_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    followed_discussions = Nested('DiscussionSchema', many=True)
    owned_invitations = Nested('InvitationSchema', many=True)
    partnered_invitations = Nested('InvitationSchema', many=True)


create_user_schema = CreateUserSchema()
edit_user_schema = EditUserSchema()
user_schema = UserSchema()