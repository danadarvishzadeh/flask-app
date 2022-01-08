import traceback
from marshmallow.exceptions import ValidationError

from discussion.app import db
from discussion.blueprints.users import bp, logger
from discussion.schemas.user import (CreateUserSchema,
                                                 edit_user_schema, user_schema)
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


@bp.route('/', methods=['POST'])
def create_users():
    req_json = request.get_json()
    try:
        user = CreateUserSchema().load(req_json)
    except ValidationError as e:
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

@bp.route('/', methods=['PUT', 'DELETE'])
@token_required
def edit_user_detail():
    user = g.user
    if request.method == 'PUT':
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
    else:
        user.query.delete()
        token = request.headers.get('Authorization').split()[1]
        tb = TokenBlackList(token=token)
        db.session.add(tb)
        db.session.commit()
        return jsonify({'response': 'ok!'}), 200

@bp.route('/<int:user_id>/', methods=['GET'])
def get_user_detail(user_id):
    user = User.query.get(user_id)
    if user is not None:
        return jsonify(user_schema.dump(user))
    else:
        logger.warning(f"Trying to access non-existing user with id {user_id}")
        raise ResourceDoesNotExists()

@bp.route('/discussions/<int:user_id>/', methods=['GET'])
def get_creator_discussions(user_id):
    page = request.args.get('page', 1, type=int)
    paginator = DiscussionPaginator
    paginator.filters = {'owner_id': user_id}
    return DiscussionPaginator.return_page(page, 'get_creator_discussions')

@bp.route('/login/', methods=['POST'])
def login_user():
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
    except AttributeError as e:
        raise InvalidCredentials(message='Please provide full creadentials.')
    except AttributeError:
        raise InvalidCredentials(message='Please provide full creadentials.')

@bp.route('/logout/', methods=['POST'])
@token_required
def logout_user():
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
