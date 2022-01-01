from discussion.app import db
from discussion.blueprints.auth.views import token_required
from discussion.models import (Discussion, Follow, Invitation, Participate,
                               Post, User)
from flask import Blueprint, abort, current_app, g, jsonify, request, url_for
from sqlalchemy.exc import IntegrityError

from discussion.blueprints.api import bp, logger
from discussion.blueprints.api.errors import *
from discussion.blueprints.api.schemas import (create_discussion_schema, create_invitation_schema,
                      create_post_schema, create_user_schema,
                      discussion_schema, invitation_schema, post_schema,
                      user_schema, edit_user_schema, summerised_invitation_schema,
                      summerised_post_schema)
from discussion.blueprints.api.utils import paginate_discussions, paginate_invitatinos, paginate_posts
import traceback


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
    except IntegrityError as e:
        logger.warning(f"Attempt to register user. params: {e.params[:-1]} origin: {e.orig}")
        db.session.rollback()
        raise JsonIntegrityError()
    except:
        trace_info = traceback.format_exc()
        logger.error(f"uncaught exception: {trace_info}")
        raise InvalidAttemp()
    else:
        logger.info(f"Adding user {user.username}")
        return user_schema.dumps(user)


@bp.route('/users/<int:id>/', methods=get)
def get_user_detail(id):
    user = User.query.get(id)
    if user is not None:
        return user_schema.dumps(user)
    else:
        logger.warning(f"Trying to access non-existing user with id {id}")
        raise ResourceDoesNotExists()


@bp.route('/users/<int:id>/', methods=put_delete)
@token_required
def edit_user_detail(id):
    user = User.query.get(id)
    if user.first() == g.user:
        if request.method == 'PUT':
            req_json = request.get_json()
            try:
                data = edit_user_schema.load(req_json, partial=True)
            except ValidationError as e:
                raise JsonValidationError(e)
            except:
                trace_info = traceback.format_exc()
                logger.error(f"uncaught exception: {trace_info}")
                raise InvalidAttemp()
            user.update(dict(data))
            db.session.commit()
            return user_schema.dumps(user.first())
        else:
            user.delete()
            db.session.commit()
            return jsonify({'response': 'ok!'}), 200
    else:
        raise JsonPermissionDenied()

@bp.route('/discussions/', methods=get)
def get_discussions():
    page = request.args.get('page', 1, type=int)
    data_set = Discussion.query
    return paginate_discussions(page, data_set, 'get_discussions')


@bp.route('/discussions/<int:id>/', methods=get)
def get_discussion_detail(id):
    discussion = Discussion.query.get(id)
    if discussion is not None:
        return discussion_schema.dumps(discussion)
    else:
        logger.warning(f"Trying to access non-existing discussion with id {id}")
        raise ResourceDoesNotExists()

@bp.route('/discussions/<int:id>/', methods=put_delete)
@token_required
def edit_discussion_detail(id):
    discussion = Discussion.query.get(id)
    if discussion is not None:
        if g.user.id == discussion.creator_id:
            if request.method == 'PUT':
                req_json = request.get_json()
                try:
                    data = discussion_schema.load(req_json, partial=True)
                except ValidationError as e:
                    raise JsonValidationError(e)
                except:
                    trace_info = traceback.format_exc()
                    logger.error(f"uncaught exception: {trace_info}")
                    raise InvalidAttemp()
                else:
                    discussion.update(dict(data))
                    db.session.commit()
                    return discussion_schema.dumps(discussion)
            else:
                discussion.delete()
                db.session.commit()
                return jsonify({'response': 'ok!'}), 200
        else:
            logger.warning(f"{g.user.username} attempted to edit {discussion.creator.username}'s discussioin.")
            raise JsonPermissionDenied()
    else:
        logger.warning(f"Trying to edit non-existing discussion with id {id}")
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
        return discussion_schema.dumps(discussion)
    except ValidationError as e:
        raise JsonValidationError(e)
    except IntegrityError as e:
        db.session.rollback()
        raise JsonIntegrityError()
    except:
        trace_info = traceback.format_exc()
        logger.error(f"uncaught exception: {trace_info}")
        raise InvalidAttemp()

@bp.route('/users/discussions/<int:id>/', methods=get)
def get_creator_discussions(id):
    page = request.args.get('page', 1, type=int)
    data_set = Discussion.query.filter_by(creator_id=id)
    return paginate_discussions(page, data_set, 'get_creator_discussions')


@bp.route('/posts/', methods=get)
def get_posts():
    page = request.args.get('page', 1, type=int)
    data_set = Post.query
    return paginate_posts(page, data_set, 'get_posts')


@bp.route('/posts/<int:id>/', methods=get)
def get_post_detail(id):
    post = Post.query.get(id)
    if post is not None:
        return summerised_post_schema.dumps(post)
    else:
        logger.warning(f"Trying to access non-existing post with id {id}")
        raise ResourceDoesNotExists()


@bp.route('/discussions/<int:id>/posts/', methods=get)
def get_discussion_posts(id):
    page = request.args.get('page')
    data_set = Post.query.filter_by(discussion_id=id)
    return paginate_posts(page, data_set, 'get_discussion_posts')


@bp.route('/posts/<int:id>/', methods=put_delete)
@token_required
def edit_post_details(id):
    post = Post.query.filter_by(id=id)
    if post is not None:
        if g.user.id == post.first().author_id:
            if request.method == 'PUT':
                req_json = request.get_json()
                try:
                    data = post_schema.load(req_json, partial=True)
                except ValidationError as e:
                    raise JsonValidationError(e)
                except:
                    trace_info = traceback.format_exc()
                    logger.error(f"uncaught exception: {trace_info}")
                    raise InvalidAttemp()
                post.update(dict(data))
                db.session.commit()
                return post_schema.dumps(post.first())
            else:
                Post.delete()
                db.session.commit()
                return jsonify({'response': 'ok!'}), 200
        else:
                logger.warning(f"{g.user.username} attempted to edit {post.first().author.username}'s post.")
                raise JsonPermissionDenied()
    else:
        logger.warning(f"Trying to edit non-existing post with id {id}")
        raise ResourceDoesNotExists()

@bp.route('/discussions/<int:id>/', methods=_post)
@token_required
def create_posts(id):
    req_json = request.get_json()
    discussion = Discussion.query.get(id)
    if discussion is not None:
        if discussion.creator_id == g.user.id or g.user.id in participants:
            try:
                participants = discussion.get_participant_ids()
                post = create_post_schema.load(req_json)
                post.author_id = g.user.id
                post.discussion_id = id
                db.session.add(post)
                db.session.commit()
                return summerised_post_schema.dumps(post)
            except ValidationError as e:
                raise JsonValidationError(e)
            except IntegrityError:
                db.session.rollback()
                raise JsonIntegrityError()
            except:
                trace_info = traceback.format_exc()
                logger.error(f"uncaught exception: {trace_info}")
                raise InvalidAttemp()
        else:
            logger.warning(f"{g.user.username} attempted to add posts to {discussion.creator.username}'s discussion.")
            raise JsonPermissionDenied()
    else:
        logger.warning(f"Trying to add posts to non-existing discussion with id {id}")
        raise ResourceDoesNotExists()

@bp.route('/discussions/<int:discussion_id>/invite/<int:user_id>/', methods=_post)
@token_required
def create_invitations(discussion_id, user_id):
    req_json = request.get_json()
    discussion = Discussion.query.get(discussion_id)
    if discussion is not None:
        if g.user.id == discussion.creator_id:
            try:
                invitation = create_invitation_schema.load(req_json)
                invitation.inviter_id = g.user.id
                invitation.invited_id = user_id
                invitation.discussion_id = discussion_id
                invitation.status = 'Sent'
                db.session.add(invitation)
                db.session.commit()
                return summerised_invitation_schema.dumps(invitation)
            except ValidationError as e:
                raise JsonValidationError(e)
            except IntegrityError:
                db.session.rollback()
                raise JsonIntegrityError()
            except:
                trace_info = traceback.format_exc()
                logger.error(f"uncaught exception: {trace_info}")
                raise InvalidAttemp()
        else:
            logger.warning(f"{g.user.username} attempted to invite users to {discussion.creator.username}'s discussion.")
            raise JsonPermissionDenied()
    else:
        logger.warning(f"Trying to invite users to non-existing discussion with id {id}")
        raise ResourceDoesNotExists()

@bp.route('/invitations/', methods=get)
def get_invitations():
    page = request.args.get('page')
    data_set = Invitation.query
    return paginate_invitatinos(page, data_set, 'get_invitations')

@bp.route('/invitations/<int:id>/', methods=put_delete)
@token_required
def edit_invitation_details(id):
    if request.method == 'PUT':
        invitation = Invitation.query.get(id)
        if invitation is not None:
            if invitation.invited_id == g.user.id:
                if invitation.status == 'Sent':
                    status = request.get_json().get('status')
                    if status in ('Accepted', 'Denied'):
                        invitation.status = status
                        participate = Participate()
                        participate.host_id = invitation.inviter_id
                        participate.participant_id = invitation.invited_id
                        participate.discussion_id = invitation.discussion_id
                        try:
                            db.session.add(invitation)
                            db.session.add(participate)
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
            else:
                logger.warning(f"{g.user.username} attempted to edit user {invitation.invited.username}'s invitation.")
                raise JsonPermissionDenied()
        else:
            logger.warning(f"Trying to edit to non-existing invitation with id {id}")
            raise ResourceDoesNotExists()

@bp.route('/discussions/<int:id>/follow/', methods=_post)
@token_required
def create_followes(id):
    follow = Follow.query.filter_by(follower_id=id, discussion_id=id).first()
    if follow is None:
        try:
            follow = Follow()
            follow.follower_id = g.user.id
            follow.discussion_id = id
            db.session.add(follow)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise JsonIntegrityError()
        except:
            trace_info = traceback.format_exc()
            logger.error(f"uncaught exception: {trace_info}")
            raise InvalidAttemp()
        else:
            return jsonify({'response': 'Ok!'}), 200
    else:
        raise ActionIsNotPossible('You already followed this user.')


@bp.route('/discussions/<int:id>/unfollow/', methods=_post)
@token_required
def delete_followes(id):
    follow = Follow.query.filter_by(follower_id=id, discussion_id=id).first()
    if follow is not None:
        follow.delete()
        db.session.commit()
        return jsonify({'response': 'Ok!'}), 200
    else:
        logger.warning(f"User {g.user.uasename} tried to delete non-existing follow with id {id}")
        raise ResourceDoesNotExists()