from functools import wraps
from discussion.models import Discussion, Invitation, Post
from .errors import JsonPermissionDenied, ResourceDoesNotExists, ActionIsNotPossible
from flask import g, request
from discussion.blueprints.api import logger

# def premission_to_add_posts(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         discussion = Discussion.query.get(kwargs['id'])
#         if discussion is not None:
#             participants = discussion.get_participant_ids()
#             if g.user.id == discussion.creator_id or g.user.id in participants:
#                 return f(*args, **kwargs)
#             else:
#                 raise JsonPermissionDenied()
#         else:
#             raise ResourceDoesNotExists()
#     return decorator

# def premission_to_invite(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         discussion = Discussion.query.get(kwargs['discussion_id'])
#         if discussion is not None:
#             if g.user.id == discussion.creator_id:
#                 return f(*args, **kwargs)
#             else:
#                 raise JsonPermissionDenied()
#         else:
#             raise ResourceDoesNotExists()
#     return decorator

# def premission_to_edit_discussion(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         discussion = Discussion.query.get(kwargs['id'])
#         if discussion is not None:
#             if g.user.id == discussion.creator_id:
#                 return f(*args, **kwargs)
#             else:
#                 raise JsonPermissionDenied()
#         else:
#             raise ResourceDoesNotExists()
#     return decorator

# def premission_to_edit_post(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         post = Post.query.get(kwargs['id'])
#         if post is not None:
#             if g.user.id == post.author_id:
#                 return f(*args, **kwargs)
#             else:
#                 raise JsonPermissionDenied()
#         else:
#             raise ResourceDoesNotExists()
#     return decorator

# def permision_to_edit_invitation(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         invitation = Invitation.query.get(kwargs['id'])
#         if invitation is not None:
#             if g.user.id == invitation.invited_id:
#                 return f(*args, **kwargs)
#             else:
#                 raise JsonPermissionDenied()
#         else:
#             raise ResourceDoesNotExists()
#     return decorator

# def permision_to_delete_invitation(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         invitation = Invitation.query.get(kwargs['id'])
#         if invitation is not None:
#             if g.user.id == invitation.invited_id or g.user.id == invitation.inviter_id:
#                 return f(*args, **kwargs)
#             else:
#                 raise JsonPermissionDenied()
#         else:
#             raise ResourceDoesNotExists()
#     return decorator

# def can_follow(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         id = kwargs['id']
#         discussion = Discussion.query.get(id)
#         follow = Follow.query.filter_by(follower_id=g.user.id, discussion_id=id).first()
#         if discussion is not None:
#             if follow is None:
#                 if g.user != discussion.creators:
#                     return f(*args, **kwargs)
#                 else:
#                     raise JsonPermissionDenied()
#             else:
#                 raise ActionIsNotPossible('You already followed this user.')
#         else:
#             raise ResourceDoesNotExists()
#     return decorator




def is_creator(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        discussion = Discussion.query.get(kwargs['discussion_id'])
        if discussion is not None:
            participants = discussion.get_participant_ids()
            if g.user.id == discussion.creator_id:
                return f(*args, **kwargs)
            else:
                raise JsonPermissionDenied()
        else:
            raise ResourceDoesNotExists()
    return decorator

def is_participant(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        discussion = Discussion.query.get(kwargs['discussion_id'])
        if discussion is not None:
            participants = discussion.get_participant_ids()
            if g.user.id in participants:
                return f(*args, **kwargs)
            else:
                raise JsonPermissionDenied()
        else:
            raise ResourceDoesNotExists()
    return decorator

def is_author(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        post = Post.query.get(kwargs['post_id'])
        if post is not None:
            if g.user.id == post.author_id:
                return f(*args, **kwargs)
            else:
                raise JsonPermissionDenied()
        else:
            raise ResourceDoesNotExists()
    return decorator

def is_invited(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        invitation = Invitation.query.get(kwargs['invitation_id'])
        if invitation is not None:
            if g.user.id == invitation.invited_id:
                return f(*args, **kwargs)
            else:
                raise JsonPermissionDenied()
        else:
            raise ResourceDoesNotExists()
    return decorator

def is_inviter(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        invitation = Invitation.query.get(kwargs['invitation_id'])
        if invitation is not None:
            if g.user.id == invitation.inviter_id:
                return f(*args, **kwargs)
            else:
                raise JsonPermissionDenied()
        else:
            raise ResourceDoesNotExists()
    return decorator

def is_creator_or_participant(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        discussion = Discussion.query.get(kwargs['discussion_id'])
        if discussion is not None:
            participants = discussion.get_participant_ids()
            if g.user.id in participants or g.user.id == discussion.creator_id:
                return f(*args, **kwargs)
            else:
                raise JsonPermissionDenied()
        else:
            raise ResourceDoesNotExists()
    return decorator

def is_inviter_or_invited(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        invitation = Invitation.query.get(kwargs['invitation_id'])
        if invitation is not None:
            if g.user.id == invitation.inviter_id or g.user.id == invitation.invited_id:
                return f(*args, **kwargs)
            else:
                raise JsonPermissionDenied()
        else:
            raise ResourceDoesNotExists()
    return decorator

def is_not_creator_nor_follower(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        discussion = Discussion.query.get(kwargs.get('discussion_id'))
        if discussion is not None:
            if g.user.id != discussion.creator_id and g.user.id not in discusison.get_follower_ids():
                return f(*args, **kwargs)
            else:
                raise ActionIsNotPossible('You can not follow this discusison.')
        else:
            raise ResourceDoesNotExists()
    return decorator

def is_follower(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        discussion = Discussion.query.get(kwargs.get('discussion_id'))
        if discussion is not None:
            if g.user.id in discusison.get_follower_ids():
                return f(*args, **kwargs)
            else:
                raise ActionIsNotPossible('You can not unfollow this discusison.')
        else:
            raise ResourceDoesNotExists()
    return decorator