import traceback

from discussion.app import db
from discussion.blueprints.api import bp, logger
from discussion.blueprints.api.errors import *
from discussion.blueprints.api.schemas import (create_discussion_schema,
                                               create_invitation_schema,
                                               create_post_schema,
                                               create_user_schema,
                                               discussion_schema,
                                               edit_user_schema,
                                               invitation_schema, post_schema,
                                               summerised_invitation_schema,
                                               summerised_post_schema,
                                               user_schema)
from discussion.blueprints.api.utils import (paginate_discussions,
                                             paginate_invitatinos,
                                             paginate_posts)
from discussion.blueprints.auth.views import token_required
from discussion.models import (Discussion, Follow, Invitation, Participate,
                               Post, User)
from flask import Blueprint, abort, current_app, g, jsonify, request, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from .permissions import permission_required

get, _post, put_delete = ['GET'], ['POST'], ['PUT', 'DELETE']


@bp.route('/users/', methods=_post)
def create_users():
    req_json = request.get_json()
    try:
        user = create_user_schema.load(req_json)
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


@bp.route('/users/<int:user_id>/', methods=get)
def get_user_detail(user_id):
    user = User.query.get(user_id)
    if user is not None:
        return jsonify(user_schema.dumps(user))
    else:
        logger.warning(f"Trying to access non-existing user with id {user_id}")
        raise ResourceDoesNotExists()


@bp.route('/users/', methods=put_delete)
@token_required
def edit_user_detail():
    user = g.user
    if request.method == 'PUT':
        req_json = request.get_json()
        try:
            data = edit_user_schema.load(req_json, partial=True)
            user.query.update(dict(data))
            db.session.commit()
            return jsonify(user_schema.dump(user).first())
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
        db.session.commit()
        return jsonify({'response': 'ok!'}), 200

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
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
    else:
        discussion.query.delete()
        db.session.commit()
        return jsonify({'response': 'ok!'}), 200
        raise JsonPermissionDenied()

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

@bp.route('/users/discussions/<int:user_id>/', methods=get)
def get_creator_discussions(user_id):
    page = request.args.get('page', 1, type=int)
    data_set = Discussion.query.filter_by(creator_id=user_id)
    return paginate_discussions(page, data_set, 'get_creator_discussions')

@bp.route('/discussions/<int:discussion_id>/posts/', methods=get)
def get_discussion_posts(discussion_id):
    page = request.args.get('page')
    data_set = Post.query.filter_by(discussion_id=discussion_id)
    return paginate_posts(page, data_set, 'get_discussion_posts')

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
@permission_required(should_have=['IsAuthor'])
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

@bp.route('/discussions/<int:discussion_id>/', methods=_post)
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

@bp.route('/discussions/<int:discussion_id>/invite/<int:user_id>/', methods=_post)
@token_required
def create_invitations(discussion_id, user_id):
    req_json = request.get_json()
    discussion = Discussion.query.get(discussion_id)
    try:
        invitation = create_invitation_schema.load(req_json)
        invitation.inviter_id = g.user.id
        invitation.invited_id = user_id
        invitation.discussion_id = discussion_id
        invitation.status = 'Sent'
        db.session.add(invitation)
        db.session.commit()
        return jsonify(summerised_invitation_schema.dump(invitation))
    except ValidationError as e:
        raise JsonValidationError(e)
    except IntegrityError:
        db.session.rollback()
        raise JsonIntegrityError()
    except:
        trace_info = traceback.format_exc()
        logger.error(f"uncaught exception: {trace_info}")
        raise InvalidAttemp()

@bp.route('/invitations/', methods=get)
@token_required
def get_invitations():
    page = request.args.get('page')
    print(g.user.id)
    print(g.user.username)
    data_set = db.session.query(Invitation).filter(or_(Invitation.invited_id==g.user.id, Invitation.inviter_id==g.user.id))
    return paginate_invitatinos(page, data_set, 'get_invitations')

@bp.route('/invitations/<int:invitation_id>/', methods=['PUT'])
@token_required
def edit_invitation_details(invitation_id):
    invitation = Invitation.query.get(invitation_id)
    if invitation.status == 'Sent':
        status = request.get_json().get('status')
        if status == 'Accepted':
            invitation.query.update({'status':status})
            participate = Participate()
            participate.host_id = invitation.inviter_id
            participate.participant_id = invitation.invited_id
            participate.discussion_id = invitation.discussion_id
            db.session.add(participate)
        elif status == 'Rejected':
            invitation.query.update({'status':status})
        else:
            raise JsonValidationError('Provide a valid answer. ["Accepted", "Rejected"]')
        try:
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
        raise ActionIsNotPossible('The action that you requested can not be done.')

@bp.route('/invitations/<int:invitation_id>/', methods=['DELETE'])
@token_required
def delete_invitation(invitation_id):
    if g.user == invitation.invited or g.user == invitation.inviter:
        invitation.query.delete()
        db.session.commit()
        return jsonify({'response': 'Ok!'}), 200
    else:
        logger.warning(f"{g.user.username} attempted to edit user {invitation.invited.username}'s invitation.")
        raise JsonPermissionDenied()

@bp.route('/discussions/<int:discussion_id>/follow/', methods=_post)
@token_required
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
def delete_followes(discussion_id):
    follow.query.delete()
    db.session.commit()
    return jsonify({'response': 'Ok!'}), 200
