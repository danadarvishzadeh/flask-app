from discussion.app import db
from discussion.blueprints.follow import bp, logger
from discussion.errors import (ActionIsNotPossible, InvalidAttemp,
                               JsonIntegrityError, JsonValidationError,
                               ResourceDoesNotExists)
from discussion.models.follow import Follow
from discussion.utils import permission_required, token_required
from flask import g, jsonify
from discussion.models.discussion import Discussion
from sqlalchemy.exc import IntegrityError
import traceback

@bp.route('/discussions/<int:discussion_id>/follow/', methods=['POST'])
@token_required
@permission_required(shouldnt_have=['IsCreator'])
def create_follows(discussion_id):
    follow = Follow.query.filter_by(follower_id=g.user.id, discussion_id=discussion_id).first()
    discussion = Discussion.query.get(discussion_id)
    try:
        follow = Follow()
        follow.follower_id = g.user.id
        follow.discussion_id = discussion_id
        db.session.add(follow)
        db.session.commit()
        return jsonify({'response': 'Ok!'}), 200
    except IntegrityError:
        db.session.rollback()
        raise JsonIntegrityError()
    except:
        trace_info = traceback.format_exc()
        logger.error(f"uncaught exception: {trace_info}")
        raise InvalidAttemp()


@bp.route('/<int:discussion_id>/', methods=['DELETE'])
@token_required
@permission_required(should_have=['IsFollower'])
def delete_follows(discussion_id):
    follow = Follow.query.filter_by(discussion_id=discussion_id).delete()
    db.session.commit()
    return jsonify({'response': 'Ok!'}), 200
