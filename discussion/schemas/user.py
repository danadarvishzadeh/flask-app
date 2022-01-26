from flask_marshmallow import Schema
from marshmallow.fields import Nested, Integer, Str, Email, IP
from marshmallow import validate
from marshmallow.decorators import post_load



class BaseUserSchema(Schema):

    first_name = Str(required=True, validate=[validate.Length(min=2, max=24)])
    last_name = Str(required=True, validate=[validate.Length(min=4, max=24)])

    @post_load
    def lowercasing(self, data, **kwargs):
        for field in self.Meta.__lower_fields__:
            if field in data:
                data[field] = data[field].lower()
        return data


class CreateUserSchema(BaseUserSchema):
    
    class Meta:
        __lower_fields__ = (
            'username',
            'first_name',
            'last_name'
        )
    
    email = Email(required=True, validate=[validate.Email()])
    password = Str(required=True, validate=[validate.Length(min=8, max=24)])
    username = Str(required=True, validate=[validate.Length(min=6, max=24)])
    

class EditUserSchema(BaseUserSchema):
    class Meta:
        __lower_fields__ = (
            'first_name',
            'last_name'
        )
    first_name = Str()
    last_name = Str()


class UserProfileSchema(BaseUserSchema):
    id = Integer()
    email = Email()
    username = Str()
    participated_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    hosted_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    owned_discussions = Nested('DiscussionSchema', only=("id", "title", "description", 'participants', 'followed_by'), many=True)
    followed_discussions = Nested('DiscussionSchema', many=True)
    owned_invitations = Nested('InvitationSchema', many=True)
    partnered_invitations = Nested('InvitationSchema', many=True)


class UserPrivateProfile(UserProfileSchema):
    # Some additional fields
    pass

class UserSchema(BaseUserSchema):
    id = Integer()
    email = Email()
    username = Str()


class UserLoginSchema(Schema):
    password = Str(required=True, validate=[validate.Length(min=8, max=24)])
    username = Str(required=True, validate=[validate.Length(min=6, max=24)])


class LoginResponse(Schema):
    access_token = Str()
    refresh_token = Str()


class RefreshTokenSchema(Schema):
    refresh_token = Str()


class SessionSchema(Schema):
    user_id = Integer()
    # ip = IP()
    ip = Str()
    client = Str()