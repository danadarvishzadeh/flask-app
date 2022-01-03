from discussion.app import db
from discussion.blueprints.follow import bp, logger
from discussion.errors import (ActionIsNotPossible, InvalidAttemp,
                               JsonIntegrityError, JsonValidationError,
                               ResourceDoesNotExists)
from discussion.models.follow import Follow
from discussion.utils import permission_required, token_required
from flask import g
from sqlalchemy.exc import IntegrityError


@bp.route('/discussions/<int:discussion_id>/follow/', methods=['POST'])
@token_required
@permission_required(shouldnt_have=['IsCreator', 'IsFollower'])
def create_follows(discussion_id):
    follow = Follow.query.filter_by(follower_id=g.user.id, discussion_id=discussion_id).first()
    discussion = Discussion.query.get(id)
    if follow is None and discussion is not None and g.user != discussion.creator:
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
    else:
        raise ActionIsNotPossible('You already followed this user.')


@bp.route('/discussions/<int:discussion_id>/unfollow/', methods=['POST'])
@token_required
@permission_required(shouldnt_have=['IsFollower'])
def delete_followes(discussion_id):
    follow.query.delete()
    db.session.commit()
    return jsonify({'response': 'Ok!'}), 200
