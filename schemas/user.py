
from flask_marshmallow import Schema, fields
from marshmallow.fields import Nested, DateTime, Integer, Str, Email
from marshmallow import validate
from marshmallow.decorators import post_dump, post_load, pre_load
from werkzeug.security import generate_password_hash

# from discussion.app import ma
from discussion.models.follow import Follow
from discussion.models.participate import Participate
from discussion.models.user import User




class CreateUserSchema(Schema):
    first_name = Str(required=True, validate=[validate.Length(min=2, max=24)])
    last_name = Str(required=True, validate=[validate.Length(min=4, max=24)])
    email = Email(required=True, validate=[validate.Email()])
    password = Str(required=True, validate=[validate.Length(min=8, max=24)])
    username = Str(required=True, validate=[validate.Length(min=6, max=24)])
    
    @post_load
    def lower_case(self, data, **kwargs):
        data['username'] = data['username'].lower()
        data['first_name'] = data['first_name'].lower()
        data['last_name'] = data['last_name'].lower()
        return data


class EditUserSchema(Schema):
    first_name = Str(validate=[validate.Length(min=2, max=24)])
    last_name = Str(validate=[validate.Length(min=4, max=24)])

    @post_load
    def lower_case(self, data, **kwargs):
        data['first_name'] = data['first_name'].lower()
        data['last_name'] = data['last_name'].lower()
        return data


class UserProfileSchema(Schema):
    id = Integer()
    first_name = Str(validate=[validate.Length(min=2, max=24)])
    last_name = Str(validate=[validate.Length(min=4, max=24)])
    email = Email()
    username = Str()
    participated_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    hosted_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    owned_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    followed_discussions = Nested('DiscussionSchema', many=True)
    owned_invitations = Nested('InvitationSchema', many=True)
    partnered_invitations = Nested('InvitationSchema', many=True)


class UserSchema(Schema):
    id = Integer()
    email = Email()
    username = Str()
    first_name = Str()
    last_name = Str()


class UserLoginSchema(Schema):
    password = Str(required=True, validate=[validate.Length(min=8, max=24)])
    username = Str(required=True, validate=[validate.Length(min=6, max=24)])


class LoginResponse(Schema):
    token = Str()