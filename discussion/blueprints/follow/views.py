@bp.route('/discussions/<int:discussion_id>/follow/', methods=_post)
@token_required
@is_not_creator_nor_follower
def create_followes(discussion_id):
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


@bp.route('/discussions/<int:discussion_id>/unfollow/', methods=_post)
@token_required
@is_follower
def delete_followes(discussion_id):
    follow.query.delete()
    db.session.commit()
    return jsonify({'response': 'Ok!'}), 200
