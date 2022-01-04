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

@bp.route('/', methods=['GET'])
def get_discussions():
    page = request.args.get('page', 1, type=int)
    data_set = Discussion.query
    return paginate_discussions(page, data_set, 'get_discussions')


@bp.route('/<int:discussion_id>/', methods=['GET'])
def get_discussion_detail(discussion_id):
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
    data_set = Post.query.filter_by(discussion_id=discussion_id)
    return paginate_posts(page, data_set, 'get_discussion_posts')
