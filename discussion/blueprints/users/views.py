from discussion.extentions import db
from discussion.blueprints.users import bp
from discussion.models.user import User
from flask import g, request
from discussion.schemas.user import (CreateUserSchema, EditUserSchema,
                                     LoginResponse, UserLoginSchema,
                                     UserSchema, RefreshTokenSchema)
from discussion.utils.auth import authenticate, login, logout, token_required, refresh_user_token
from discussion.utils.errors import (InvalidAttemp, InvalidCredentials,
                                     InvalidToken, JsonIntegrityError,
                                     ResourceDoesNotExists)
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

@bp.route('', methods=["POST", "PUT", "DELETE"])
class UserView(MethodView):

    @bp.arguments(CreateUserSchema)
    @bp.response(200, UserSchema)
    def post(self, registration_data):
        try:
            # logger.error(url_for('uers.UserView'))
            user = User(**registration_data).save()
            logger.info(f'user {user.username} created')
            return user
        except IntegrityError as e:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            logger.exception('')
            raise InvalidAttemp()

    @token_required()
    @bp.arguments(EditUserSchema)
    @bp.response(204)
    def put(self, update_data):
        try:
            g.user.update(update_data)
            logger.info(f'user {g.user.username} chenged')
        except IntegrityError as e:
            logger.warning(f'Integrity error: {e}')
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            logger.exception('')
            raise InvalidAttemp()

    @token_required()
    @bp.response(204)
    def delete(self):
        g.user.delete()
        logger.info(f'user {g.user.username} deleted')


@bp.route('/<int:user_id>', methods=['GET'])    
class UserDetailView(MethodView):

    @bp.response(200, UserSchema)
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return user
        logger.warning(f"access non existing user_id {user_id}")
        raise ResourceDoesNotExists()


@bp.route('/login', methods=['POST'])
class LoginView(MethodView):

    @bp.arguments(UserLoginSchema, unknown='EXCLUDE')
    @bp.response(200, LoginResponse)
    def post(self, creadentials):
        if authenticate(creadentials):
            access_token, refresh_token = login()
            logger.info(f'user {g.user.username} logged in')
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
            }
        logger.warning(f'Invalid credentials: {creadentials}')
        raise InvalidCredentials(message='Username or Password you provided are invalid.')


@bp.route('/logout', methods=["GET"])
class LogoutView(MethodView):

    @token_required()
    @bp.response(204)
    def get(self):
        try:
            logout()
            logger.info(f'user {g.user.username} logged out')
        except InvalidToken:
            raise InvalidToken('Invalid Token Provided.')
        except:
            logger.exception('')
            raise InvalidAttemp()


@bp.route('/refresh', methods=["POST"])
class RefreshTokenView(MethodView):

    @token_required(refresh=True)
    @bp.arguments(RefreshTokenSchema)
    @bp.response(200, LoginResponse)
    def post(self, refresh_token):
        try:
            access_token, refresh_token  = refresh_user_token()
            logger.info(f'user {g.user.username} refreshed token')
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
            }
        except InvalidToken:
            raise InvalidToken('Invalid Token Provided.')
        except Exception as e:
            logger.exception('')
            raise InvalidAttemp()