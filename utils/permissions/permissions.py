
from discussion.models.discussion import Discussion
from discussion.models.invitation import Invitation
from discussion.models.post import Post
from . import BasePermission
from flask import g


class IsOwner(BasePermission):
    def has_access(self):
        return g.user.id == self.resource.owner_id


class IsPartner(BasePermission):
    def has_access(self):
        return g.user.id == self.resource.partner_id


class InPartners(BasePermission):
    def has_access(self):
        return g.user in self.resource.partner_users


class IsInvited(BasePermission):
    def has_access(self):
        return g.user in self.resource.invited_users