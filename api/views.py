from flask import current_app, request, g, abort
# from discussion.auth.views import auth
from flask import Blueprint, jsonify, url_for
from discussion.app import db
from discussion.models import Discussion, Post, User, Invitation, Participate, Follow
from .schemas import (
                    create_user_schema, user_schema, discussion_schema,
                    create_discussion_schema, post_schema,
                    create_post_schema, create_invitation_schema,
                    invitation_schema,)

# from flask_jwt import jwt_required, current_identity
from .utils import paginate_discussions, paginate_posts, paginate_invitatinos
from discussion.auth.views import token_required

api_bp = Blueprint('api', __name__)

get, _post, put_delete = ['GET'], ['POST'], ['PUT', 'DELETE']


@api_bp.route('/users/', methods=_post)
def create_users():
    req_json = request.get_json()
    try:
        user = create_user_schema.load(req_json)
        db.session.add(user)
        db.session.commit()
        return user_schema.dumps(user)
    except Exception as e:
        # TODO error handling
        print(e)
        pass

@api_bp.route('/users/<int:id>/', methods=get)
def get_user_detail(id):
    user = User.query.filter_by(id=id).first()
    if user is not None:
        return user_schema.dumps(user)
    else:
        # TODO error handling
        pass


@api_bp.route('/users/<int:id>/', methods=put_delete)
@token_required
def edit_user_detail(id):
    user = User.query.filter_by(id=id)
    if user.first() == g.user:
        if request.method == 'PUT':
            req_json = request.get_json()
            data = user_schema.load(req_json, partial=True)
            user.update(dict(data))
            db.session.commit()
            return user_schema.dumps(user.first())
        else:
            user.delete()
            db.session.commit()
            return jsonify({'response': 'ok!'}), 200
    else:
        # TODO error handling
        pass


@api_bp.route('/discussions/', methods=get)
def get_discussions():
    page = request.args.get('page', 1, type=int)
    data_set = Discussion.query
    return paginate_discussions(page, data_set, 'get_discussions')


@api_bp.route('/discussions/<int:id>/', methods=get)
def get_discussion_detail(id):
    discussion = Discussion.query.get(id)
    if discussion is not None:
        return discussion_schema.dumps(discussion)
    else:
        # TODO error handling
        pass


@api_bp.route('/discussions/<int:id>/', methods=put_delete)
@token_required
def edit_discussion_detail(id):
    discussion = Discussion.query.filter_by(id=id)
    if g.user.id == discussion.first().creator_id:
        if request.method == 'PUT':
            req_json = request.get_json()
            data = discussion_schema.load(req_json, partial=True)
            discussion.update(dict(data))
            db.session.commit()
            return discussion_schema.dumps(discussion.first())
        else:
            discussion.delete()
            db.session.commit()
            return jsonify({'response': 'ok!'}), 200
    else:
        # TODO error handling
        pass


@api_bp.route('/discussions/', methods=_post)
@token_required
def create_discussions():
    req_json = request.get_json()
    try:
        discussion = create_discussion_schema.load(req_json)
        discussion.creator_id = g.user.id
        db.session.add(discussion)
        db.session.commit()
        return discussion_schema.dumps(discussion)
    except Exception as e:
        print(e)
        # TODO error handling
        pass


@api_bp.route('/users/discussions/<int:id>/', methods=get)
def get_creator_discussions(id):
    page = request.args.get('page', 1, type=int)
    data_set = Discussion.query.filter_by(creator_id=id)
    return paginate_discussions(page, data_set, 'get_creator_discussions')


@api_bp.route('/posts/', methods=get)
def get_posts():
    page = request.args.get('page', 1, type=int)
    data_set = Post.query
    return paginate_posts(page, data_set, 'get_posts')


@api_bp.route('/posts/<int:id>/', methods=get)
def get_post_detail(id):
    post = Post.query.get(id)
    if post is not None:
        return post_schema.dumps(post)
    else:
        # TODO error handling
        pass


@api_bp.route('/discussions/<int:id>/posts/', methods=get)
def get_discussion_posts(id):
    page = request.args.get('page')
    data_set = Post.query.filter_by(discussion_id=id)
    return paginate_posts(page, data_set, 'get_discussion_posts')


@api_bp.route('/posts/<int:id>/', methods=put_delete)
@token_required
def edit_post_details(id):
    post = Post.query.filter_by(id=id)
    if g.user.id == post.first().author_id:
        if request.method == 'PUT':
            req_json = request.get_json()
            data = post_schema.load(req_json, partial=True)
            post.update(dict(data))
            db.session.commit()
            return post_schema.dumps(post.first())
        else:
            Post.delete()
            db.session.commit()
            return jsonify({'response': 'ok!'}), 200
    else:
        # TODO error handling
        pass


@api_bp.route('/discussions/<int:id>/', methods=_post)
@token_required
def create_posts(id):
    req_json = request.get_json()
    discussion = Discussion.query.get(id)
    if discussion is not None and discussion.creator_id == g.user.id:
        try:
            post = create_post_schema.load(req_json)
            post.author_id = g.user.id
            post.discussion_id = id
            db.session.add(post)
            db.session.commit()
            return post_schema.dumps(post)
        except Exception as e:
            raise e
            # TODO error handling
            pass
    else:
        # TODO
        pass

@api_bp.route('/discussions/<int:discussion_id>/invite/<int:user_id>/', methods=_post)
@token_required
def create_invitations(discussion_id, user_id):
    req_json = request.get_json()
    discussion = Discussion.query.get(discussion_id)
    if g.user.id == discussion.creator_id:
        try:
            invitation = create_invitation_schema.load(req_json)
            invitation.inviter_id = g.user.id
            invitation.invited_id = user_id
            invitation.discussion_id = discussion_id
            invitation.status = 'Sent'
            db.session.add(invitation)
            db.session.commit()
            return invitation_schema.dumps(invitation)
        except Exception as e:
            print(e)
            #TODO error handling
            pass
    else:
        #TODO
        pass

@api_bp.route('/invitations/', methods=get)
def get_invitations():
    page = request.args.get('page')
    data_set = Invitation.query
    return paginate_invitatinos(page, data_set, 'get_invitations')


@api_bp.route('/invitations/<int:id>/', methods=put_delete)
@token_required
def edit_invitation_details(id):
    if request.method == 'PUT':
        invitation = Invitation.query.get(id)
        if invitation is not None and invitation.invited_id == g.user.id:
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
                    except Exception as e:
                        print(e)
                        #TODO error handling
                        pass

@api_bp.route('/discussions/<int:id>/follow/', methods=_post)
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
            return jsonify({'response': 'Ok!'}), 200
        except Exception as e:
            print(e)
            #TODO error handling
            pass

@api_bp.route('/discussions/<int:id>/unfollow/', methods=_post)
@token_required
def delete_followes(id):
    follow = Follow.query.filter_by(follower_id=id, discussion_id=id).first()
    if follow is not None:
        try:
            follow.delete()
            db.session.commit()
            return jsonify({'response': 'Ok!'}), 200
        except Exception as e:
            print(e)
            #TODO error handling
            pass