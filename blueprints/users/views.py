import traceback
from marshmallow.exceptions import ValidationError

from discussion.app import db
from discussion.blueprints.users import bp, logger
from discussion.schemas.user import (CreateUserSchema, SummerisedUserSchema,
                                                 edit_user_schema, user_schema, EditUserSchema, UserSchema)
from discussion.utils.errors import (InvalidAttemp, InvalidCredentials,
                               JsonIntegrityError, JsonValidationError,
                               ResourceDoesNotExists)
from discussion.models.tokenblacklist import TokenBlackList
from discussion.models.user import User
from discussion.models.discussion import Discussion
from discussion.utils.perms.decorators import permission_required
from discussion.utils.auth import token_required, decode_auth_token, encode_auth_token
from flask import current_app, g, jsonify, request
from sqlalchemy.exc import IntegrityError
from discussion.blueprints.discussions.paginators import DiscussionPaginator
from flasgger import SwaggerView
from discussion.schemas.response import ErrorSchema, OkResponse


class UserCreationView(SwaggerView): 

    tags = ['user']

    parameters = [
        {
            "name": "user",
            "in": "body",
            "type": "object",
            "schema": CreateUserSchema
        }
    ]
    validate = True

    responses = {
        200: {
            "description": "Created user.",
            "schema": UserSchema
        },
        400: {
            "description": "Invalid input.",
            "schema": ErrorSchema
        },
        500: {
            "description": "Invalid attemp.",
            "schema": ErrorSchema
        },
    }

    def post(self):
        req_json = request.get_json()
        try:
            user = CreateUserSchema().load(req_json)
        except ValidationError as e:
            print(e)
            raise JsonValidationError(e)
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
        db.session.add(user)
        try:
            db.session.commit()
            logger.info(f"Adding user {user.username}")
            return jsonify(user_schema.dump(user))
        except IntegrityError as e:
            logger.warning(f"Attempt to register user. params: {e.params[:-1]} origin: {e.orig}")
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    

bp.add_url_rule('/', view_func=UserCreationView.as_view('create_users'), methods=["POST"])

# @bp.route('/', methods=['PUT', 'DELETE'])
# @token_required
# def edit_user_detail():
#     user = g.user
#     if request.method == 'PUT':
#         req_json = request.get_json()
#         try:
#             data = edit_user_schema.load(req_json, partial=True)
#             user.query.update(dict(data))
#             db.session.commit()
#             return jsonify(user_schema.dump(user))
#         except ValidationError as e:
#             raise JsonValidationError(e)
#         except IntegrityError as e:
#             db.session.rollback()
#             raise JsonIntegrityError()
#         except:
#             trace_info = traceback.format_exc()
#             logger.error(f"uncaught exception: {trace_info}")
#             raise InvalidAttemp()
#     else:
#         user.query.delete()
#         token = request.headers.get('Authorization').split()[1]
#         tb = TokenBlackList(token=token)
#         db.session.add(tb)
#         db.session.commit()
#         return jsonify({'response': 'ok!'}), 200


class UserChangeView(SwaggerView):
    decorators = [token_required]
    tags = ['user']
    parameters = [
        {
            "name": "edit data",
            "in": "body",
            "type": "object",
            "schema": EditUserSchema
        }
    ]
    validate = True

    responses = {
        200: {
            "description": "Ok.",
            "schema": OkResponse
        },
        400: {
            "description": "Invalid input.",
            "schema": ErrorSchema
        },
        404: {
            "description": "User not found.",
            "schema": ErrorSchema
        },
    }

    def put(self):
        user = g.user
        req_json = request.get_json()
        try:
            data = edit_user_schema.load(req_json, partial=True)
            user.query.update(dict(data))
            db.session.commit()
            return jsonify(user_schema.dump(user))
        except ValidationError as e:
            raise JsonValidationError(e)
        except IntegrityError as e:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()

    def delete(self):
        user = g.user
        user.query.delete()
        token = request.headers.get('Authorization').split()[1]
        tb = TokenBlackList(token=token)
        db.session.add(tb)
        db.session.commit()
        return jsonify({'response': 'ok!'}), 200

class UserDetailView(SwaggerView):
    tags = ['user']
    parameters = [
        {
            "in": "path",
            "name": "user_id",
            "description": "Id of expected user.",
            "type": "integer",
        }
    ]

    responses = {
        200: {
            "description": "Created user.",
            "schema": UserSchema
        },
        400: {
            "description": "Bad request.",
            "schema": ErrorSchema
        }
    }

    def get(self, user_id):
        user = User.query.get(user_id)
        if user is not None:
            return jsonify(user_schema.dump(user))
        else:
            logger.warning(f"Trying to access non-existing user with id {user_id}")
            raise ResourceDoesNotExists()


class LoginView(SwaggerView):
    tags = ['user']
    parameters = [
        {
            "in": "body",
            "name": "username",
            "type": "string"
        },
        {
            "in": "body",
            "name": "password",
            "type": "string"
        }
    ]

    responses = {
        200: {
            "description": "successful login.",
            "schema": {
                "type": "string"
            }
        },
        400: {
            "description": "Invalid credentials.",
            "schema": ErrorSchema
        }
    }
    # @bp.route('/login/', methods=['POST'])
    def post(self):
        try:
            auth_token = request.headers.get('Authorization').split()[1]
            user = decode_auth_token(auth_token)
        except:
            pass
        else:
            if user is not None:
                logger.info(f"User {user.username} tried log in, having valid token.")
                raise InvalidCredentials(message='You have a already registered token and hence, logged in.')
            else:
                logger.info(f"User with depricated token {auth_token} tried log in, having invalid token.")
                raise InvalidCredentials(message='The Token you provided is invalid.')
        req_json = request.get_json()
        try:
            user = User.query.filter_by(username=req_json['username']).first()
            if user.password_check(req_json['password']):
                token = encode_auth_token(user)
                logger.info(f"User {user.username} logged in.")
                return jsonify({
                    'token': token
                })
            else:
                raise InvalidCredentials(message='Username or Password you provided are invalid.')
        except AttributeError:
            raise InvalidCredentials(message='Please provide full creadentials.')

class LogOutView(SwaggerView):
    tags = ['user']
    decorators = [token_required]
    responses = {
        200: {
            "description": "successful logout.",
        },
        401: {
            "description": "Invalid credentials.",
            "schema": ErrorSchema
        }
    }
    # @bp.route('/logout/', methods=['POST'])
    # @token_required
    def get(self):
        try:
            token = request.headers.get('Authorization').split()[1]
            tb = TokenBlackList(token=token)
            db.session.add(tb)
            db.session.commit()
            return jsonify({
                "response": "Ok!"
            })
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()

