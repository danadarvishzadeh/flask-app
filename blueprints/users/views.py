import traceback

from discussion.app import db
from discussion.blueprints.users import bp, logger
from discussion.models.discussion import Discussion
from discussion.models.tokenblacklist import TokenBlackList
from discussion.models.user import User
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.schemas.user import (CreateUserSchema, EditUserSchema,
                                     UserSchema, edit_user_schema, user_schema)
from discussion.utils.auth import authenticate, login, logout, token_required
from discussion.utils.errors import (InvalidAttemp, InvalidCredentials,
                                     InvalidToken, JsonIntegrityError,
                                     JsonValidationError,
                                     ResourceDoesNotExists)
from discussion.utils.paginators.discussion import DiscussionPaginator
from discussion.utils.permissions.decorators import permission_required
from flasgger import SwaggerView
from flask import current_app, g, jsonify, request
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError


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
            user.save()
            return jsonify(user_schema.dump(user))
        except IntegrityError as e:
            logger.warning(f"Attempt to register user. params: {e.params[:-1]} origin: {e.orig}")
            db.session.rollback()
            raise JsonIntegrityError()
        except ValidationError as e:
            raise JsonValidationError(e)
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()


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
            user = g.user.update(data)
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
        g.user.delete()
        return jsonify({'response': 'ok!'}), 200

class UserDetailView(SwaggerView):
    tags = ['user']
    parameters = [
        {
            "in": "path",
            "name": "user_id",
            "description": "Id of expected user.",
            "type": "integer",
            "required": "True",
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
        if user:
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
            "schema": OkResponse
        },
        400: {
            "description": "Invalid credentials.",
            "schema": ErrorSchema
        }
    }

    def post(self):
        token = request.headers.get('Authorization').split()
        req_json = request.get_json()
        username = req_json.get('username')
        password = req_json.get('password')
        if authenticate(username, password):
            token = login(token)
            return jsonify({
                    'token': token
                })    
        else:
            raise InvalidCredentials(message='Username or Password you provided are invalid.')


class LogOutView(SwaggerView):
    tags = ['user']
    decorators = [token_required]
    parameters = [
        {
            "in": "header",
            "name": "Authorization",
            "type": "string",
            "required": "true"
        }
    ]
    responses = {
        200: {
            "description": "successful logout.",
        },
        401: {
            "description": "Invalid credentials.",
            "schema": ErrorSchema
        }
    }
    def get(self):
        token = request.headers.get('Authorization')
        try:
            logout(g.user, token)
        except InvalidToken:
            raise InvalidToken()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
        else:
            return jsonify({
                "response": "Ok!"
            })


bp.add_url_rule('/<int:user_id>/',
                view_func=UserDetailView.as_view('get_user_detailes'),
                methods=["GET"])

bp.add_url_rule('/',
                view_func=UserCreationView.as_view('create_users'),
                methods=["POST"])

bp.add_url_rule('/<int:user_id>/',
                view_func=UserChangeView.as_view('edit_user_details'),
                methods=["PUT", "DELETE"])

bp.add_url_rule('/login/',
                view_func=LoginView.as_view('login_user'),
                methods=["POST"])

bp.add_url_rule('/logout/',
                view_func=LogOutView.as_view('logout_user'),
                methods=["GET"])
