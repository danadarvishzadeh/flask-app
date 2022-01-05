from discussion.app import db
from discussion.blueprints.discussions import bp, logger
from discussion.blueprints.discussions.schemas import (
    create_discussion_schema, discussion_schema)
from discussion.errors import (ActionIsNotPossible, InvalidAttemp,
                               JsonIntegrityError, JsonValidationError,
                               ResourceDoesNotExists)
from discussion.models.discussion import Discussion
from discussion.models.post import Post
from discussion.utils import permission_required, token_required
from flask import g, request, jsonify
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
import traceback
from discussion.blueprints.discussions.paginators import DiscussionPaginator
from discussion.blueprints.posts.paginators import PostPaginator

@bp.route('/', methods=['GET'])
def get_discussions():
    """ Returns list of discussions
    ---
    responses:
        200:
            description: A paginated list of discussions
            schema:
                id: Discussion
                items:
                    $ref: '#/definitions/Discussion'
            examples:
                {
                "creator": {
                    "email": "ali@dana.ir",
                    "id": 3,
                    "lastname": "danad",
                    "name": "ali",
                    "username": "ali"
                },
                "date_created": "2022-01-04T08:40:33.539633",
                "description": "fifth description",
                "followed_by": [],
                "id": 1,
                "invitations": [
                    {
                        "body": "I'll be happy to talk about this...",
                        "id": 1,
                        "invited": {
                            "email": "mamad@dana.ir",
                            "id": 2,
                            "lastname": "danad",
                            "name": "mamad",
                            "username": "mamad"
                        },
                        "status": "Sent"
                    }
                ],
                "participants": [],
                "posts": [],
                "title": "fifth discussion"
            }
    """
    page = request.args.get('page', 1, type=int)
    return DiscussionPaginator.return_page(page, 'get_discussions')


@bp.route('/<int:discussion_id>/', methods=['GET'])
def get_discussion_detail(discussion_id):
    """Find discussions by id
    ---
    parameters:
        -   name: discussion_id
            in: path
            type: integer
            required: true
    responses:
        200:
            description: A discussion object
            schema:
                $ref: '#/definitions/Discussion'
            examples:
                {
                "creator": {
                    "email": "ali@dana.ir",
                    "id": 3,
                    "lastname": "danad",
                    "name": "ali",
                    "username": "ali"
                },
                "date_created": "2022-01-04T08:40:33.539633",
                "description": "fifth description",
                "followed_by": [],
                "id": 1,
                "invitations": [
                    {
                        "body": "I'll be happy to talk about this...",
                        "id": 1,
                        "invited": {
                            "email": "mamad@dana.ir",
                            "id": 2,
                            "lastname": "danad",
                            "name": "mamad",
                            "username": "mamad"
                        },
                        "status": "Sent"
                    }
                ],
                "participants": [],
                "posts": [],
                "title": "fifth discussion"
            }
        400:
            description: A discussion object
            schema:
                $ref: '#/definitions/Discussion'
    """
    discussion = Discussion.query.get(discussion_id)
    if discussion is not None:
        return jsonify(discussion_schema.dump(discussion))
    else:
        logger.warning(f"Trying to access non-existing discussion with id {discussion_id}")
        raise ResourceDoesNotExists()

@bp.route('/<int:discussion_id>/', methods=['PUT', 'DELETE'])
@token_required
@permission_required(should_have=['IsCreator'])
def edit_discussion_detail(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    if request.method == 'PUT':
        req_json = request.get_json()
        try:
            data = discussion_schema.load(req_json, partial=True)
            discussion.query.update(dict(data))
            db.session.commit()
            return jsonify(discussion_schema.dump(discussion))
        except ValidationError as e:
            raise JsonValidationError(e)
        except:
            trace_info = traceback.format_exc()
            print(logger)
            print(trace_info)
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    else:
        discussion.query.delete()
        db.session.commit()
        return jsonify({'response': 'ok!'}), 200

@bp.route('/', methods=['POST'])
@token_required
def create_discussions():
    req_json = request.get_json()
    try:
        discussion = create_discussion_schema.load(req_json)
        discussion.creator_id = g.user.id
        db.session.add(discussion)
        db.session.commit()
        return jsonify(discussion_schema.dump(discussion))
    except ValidationError as e:
        raise JsonValidationError(e)
    except IntegrityError as e:
        db.session.rollback()
        raise JsonIntegrityError()
    except:
        trace_info = traceback.format_exc()
        logger.error(f"uncaught exception: {trace_info}")
        raise InvalidAttemp()

@bp.route('/<int:discussion_id>/posts/', methods=['GET'])
def get_discussion_posts(discussion_id):
    page = request.args.get('page')
    return PostPaginator.return_page(page, 'get_discussion_posts')
