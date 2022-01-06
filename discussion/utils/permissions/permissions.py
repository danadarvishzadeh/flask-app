from abc import ABC, abstractmethod

from flask import g

from discussion.errors import (ActionIsNotPossible, JsonPermissionDenied,
                               ResourceDoesNotExists)
from discussion.models.discussion import Discussion
from discussion.models.invitation import Invitation
from discussion.models.post import Post


class PermissionBase(ABC):
    @abstractmethod
    def has_access(self, **kwargs):
        pass


class IsCreator(PermissionBase):
    def has_access(self, **kwargs):
        discussion = Discussion.query.get(kwargs['discussion_id'])
        if discussion is not None:
            participants = discussion.get_participant_ids()
            if g.user.id == discussion.creator_id:
                return True
            else:
                return False
        else:
                raise ResourceDoesNotExists()


class IsParticipant(PermissionBase):
    def has_access(self, **kwargs):
        discussion = Discussion.query.get(kwargs['discussion_id'])
        if discussion is not None:
            participants = discussion.get_participant_ids()
            if g.user.id in participants:
                return True
            else:
                return False
        else:
            raise ResourceDoesNotExists()


class IsAuthor(PermissionBase):
    def has_access(self, **kwargs):
        post = Post.query.get(kwargs['post_id'])
        if post is not None:
            if g.user.id == post.author_id:
                return True
            else:
                return False
        else:
            raise ResourceDoesNotExists()


class IsInvited(PermissionBase):
    def has_access(self, **kwargs):
        invitation = Invitation.query.get(kwargs['invitation_id'])
        if invitation is not None:
            if g.user.id == invitation.invited_id:
                return True
            else:
                return False
        else:
            raise ResourceDoesNotExists()


class IsInviter(PermissionBase):
    def has_access(self, **kwargs):
        invitation = Invitation.query.get(kwargs['invitation_id'])
        if invitation is not None:
            if g.user.id == invitation.inviter_id:
                return True
            else:
                return False
        else:
            raise ResourceDoesNotExists()


class IsFollower(PermissionBase):
    def has_access(self, **kwargs):
        discussion = Discussion.query.get(kwargs.get('discussion_id'))
        if discussion is not None:
            if g.user.id in discussion.get_follower_ids():
                return True
            else:
                return False
        else:
            raise ResourceDoesNotExists()