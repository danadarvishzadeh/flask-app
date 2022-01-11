import traceback

from discussion.app import db
from discussion.blueprints.users import bp, logger
from discussion.models.user import User
from discussion.schemas.response import ErrorSchema, OkResponse
from discussion.schemas.user import (CreateUserSchema, EditUserSchema,
                                     LoginResponse, UserLoginSchema,
                                     UserSchema)
from discussion.utils.auth import authenticate, login, logout, token_required
from discussion.utils.errors import (InvalidAttemp, InvalidCredentials,
                                     InvalidToken, JsonIntegrityError,
                                     ResourceDoesNotExists)
from discussion.utils.permissions.decorators import permission_required
from flask import g, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError


@bp.route('', methods=["POST", "PUT", "DELETE"])
class UserView(MethodView):

    @bp.arguments(CreateUserSchema)
    @bp.response(200, UserSchema)
    def post(self, registration_data):
        try:
            logger.info('here')
            return User(registration_data).save()
        except IntegrityError as e:
            logger.warning(f"Attempt to register user. params: {e.params[:-1]} origin: {e.orig}")
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            print(traceback)
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()

    @token_required
    @bp.arguments(EditUserSchema)
    @bp.response(204)
    def put(self, update_data):
        try:
            g.user.update(update_data)
        except IntegrityError as e:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()

    @token_required
    @bp.response(204)
    def delete(self):
        g.user.delete()


@bp.route('/<int:user_id>', methods=['GET'])    
class UserDetailView(MethodView):

    @bp.response(200, UserSchema)
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return user
        logger.warning(f"Trying to access non-existing user with id {user_id}")
        raise ResourceDoesNotExists()


@bp.route('/login', methods=['POST'])
class LoginView(MethodView):

    @bp.arguments(UserLoginSchema)
    @bp.response(200, LoginResponse)
    def post(self, creadentials):
        if authenticate(creadentials):
            token = login()
            return {'token':token}
        raise InvalidCredentials(message='Username or Password you provided are invalid.')


@bp.route('/logout', methods=["GET"])
class LogOutView(MethodView):

    @token_required
    @bp.response(204)
    def get(self):
        token = request.headers.get('Authorization')
        try:
            logout(token)
        except InvalidToken:
            raise InvalidToken()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
