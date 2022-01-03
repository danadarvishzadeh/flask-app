import traceback

from discussion.app import db
from discussion.blueprints.invite import bp, logger
from discussion.blueprints.invite.schemas import (invitation_schema,
                                                  summerised_invitation_schema)
from discussion.blueprints.users.views import token_required
from discussion.models import (Discussion, Follow, Invitation, Participate,
                               Post, User)
from discussion.utils import paginate_invitations
from flask import jsonify, request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError


@bp.route('/posts/', methods=get)
def get_posts():
    page = request.args.get('page', 1, type=int)
    data_set = Post.query
    return paginate_posts(page, data_set, 'get_posts')

@bp.route('/posts/<int:discussion_id>/', methods=get)
def get_post_detail(discussion_id):
    post = Post.query.get(discussion_id)
    if post is not None:
        return jsonify(summerised_post_schema.dump(post))
    else:
        logger.warning(f"Trying to access non-existing post with id {discussion_id}")
        raise ResourceDoesNotExists()

@bp.route('/posts/<int:post_id>/', methods=put_delete)
@token_required
@is_author
def edit_post_details(post_id):
    post = Post.query.get(post_id)
    if post is not None:
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
    else:
        logger.warning(f"Trying to edit non-existing post with id {post_id}")
        raise ResourceDoesNotExists()

@bp.route('/posts/<int:discussion_id>/', methods=_post)
@token_required
@is_creator_or_participant
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
