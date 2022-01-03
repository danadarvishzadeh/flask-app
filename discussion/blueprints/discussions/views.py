@bp.route('/discussions/', methods=get)
def get_discussions():
    page = request.args.get('page', 1, type=int)
    data_set = Discussion.query
    return paginate_discussions(page, data_set, 'get_discussions')


@bp.route('/discussions/<int:discussion_id>/', methods=get)
def get_discussion_detail(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    if discussion is not None:
        return jsonify(discussion_schema.dump(discussion))
    else:
        logger.warning(f"Trying to access non-existing discussion with id {discussion_id}")
        raise ResourceDoesNotExists()

@bp.route('/discussions/<int:discussion_id>/', methods=put_delete)
@token_required
@is_creator
def edit_discussion_detail(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    if discussion is not None:
        if g.user.discussion_id == discussion.creator_discussion_id:
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
                    logger.error(f"uncaught exception: {trace_info}")
                    raise InvalidAttemp()
            else:
                discussion.query.delete()
                db.session.commit()
                return jsonify({'response': 'ok!'}), 200
        else:
            logger.warning(f"{g.user.username} attempted to edit {discussion.creator.username}'s discussioin.")
            raise JsonPermissionDenied()
    else:
        logger.warning(f"Trying to edit non-existing discussion with id {discussion_id}")
        raise ResourceDoesNotExists()

@bp.route('/discussions/', methods=_post)
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

@bp.route('/discussions/<int:discussion_id>/posts/', methods=get)
def get_discussion_posts(discussion_id):
    page = request.args.get('page')
    data_set = Post.query.filter_by(discussion_id=discussion_id)
    return paginate_posts(page, data_set, 'get_discussion_posts')
