import traceback

from discussion.app import db
from discussion.blueprints.posts import bp, logger
from discussion.blueprints.posts.schemas import create_post_schema, post_schema, summerised_post_schema
from discussion.errors import (InvalidAttemp, JsonIntegrityError,
                               JsonValidationError, ResourceDoesNotExists)
from discussion.models.post import Post
from discussion.utils import permission_required, token_required
from flask import g, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow.exceptions import ValidationError
from discussion.blueprints.posts.paginators import PostPaginator

@bp.route('/', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    return PostPaginator.return_page(page, 'get_posts')

@bp.route('/<int:post_id>/', methods=['GET'])
def get_post_detail(post_id):
    post = Post.query.get(post_id)
    if post is not None:
        return jsonify(summerised_post_schema.dump(post))
    else:
        logger.warning(f"Trying to access non-existing post with id {post_id}")
        raise ResourceDoesNotExists()

@bp.route('/<int:post_id>/', methods=['PUT', 'DELETE'])
@token_required
@permission_required(should_have=['IsAuthor'])
def edit_post_details(post_id):
    post = Post.query.get(post_id)
    if request.method == 'PUT':
        req_json = request.get_json()
        try:
            data = post_schema.load(req_json, partial=True)
            post.query.update(dict(data))
            db.session.commit()
            return jsonify(post_schema.dump(post))
        except ValidationError as e:
            raise JsonValidationError(e)
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    else:
        post.query.delete()
        db.session.commit()
        return jsonify({'response': 'ok!'}), 200

@bp.route('/<int:discussion_id>/', methods=['POST'])
@token_required
@permission_required(one_of=['IsCreator', 'IsParticipant'])
def create_posts(discussion_id):
    req_json = request.get_json()
    try:
        post = create_post_schema.load(req_json)
        post.author_id = g.user.id
        post.discussion_id = discussion_id
        db.session.add(post)
        db.session.commit()
        return jsonify(summerised_post_schema.dump(post))
    except ValidationError as e:
        raise JsonValidationError(e)
    except IntegrityError:
        db.session.rollback()
        raise JsonIntegrityError()
    except:
        trace_info = traceback.format_exc()
        logger.error(f"uncaught exception: {trace_info}")
        raise InvalidAttemp()
