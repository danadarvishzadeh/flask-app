from abc import ABC, abstractmethod

from flask import g

from discussion.utils.errors import (ActionIsNotPossible, JsonPermissionDenied,
                               ResourceDoesNotExists)
from discussion.models.discussion import Discussion
from discussion.models.invitation import Invitation
from discussion.models.post import Post


class PermissionBase(ABC):

    @staticmethod
    def get_resource_id_name(resource):
        return resource.__name__.lower() + '_id'

    @abstractmethod
    def has_access(self, resource, **kwargs):
        pass


class IsOwner(PermissionBase):
    def has_access(self, resource, **kwargs):
        resource = resource.query.get(kwargs[self.get_resource_id_name(resource)])
        if resource:
            return g.user.id == resource.owner_id
        else:
            raise ResourceDoesNotExists()


class IsPartner(PermissionBase):
    def has_access(self, resource, **kwargs):
        resource = resource.query.get(kwargs[self.get_resource_id_name(resource)])
        if not resource:
            raise ResourceDoesNotExists()

        return g.user.id == resource.partner_id


class InPartners(PermissionBase):
    def has_access(self, resource, **kwargs):
        resource = resource.query.get(kwargs[self.get_resource_id_name(resource)])
        if resource is not None:
            return g.user.id in resource.partner_users
        else:
            raise ResourceDoesNotExists()