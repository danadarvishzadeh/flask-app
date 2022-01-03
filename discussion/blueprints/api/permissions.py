from functools import wraps
from discussion.models import Discussion, Invitation, Post
from .errors import JsonPermissionDenied, ResourceDoesNotExists, ActionIsNotPossible
from flask import g, request
from discussion.blueprints.api import logger




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