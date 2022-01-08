from abc import ABC, abstractmethod

from flask import g

from discussion.errors import (ActionIsNotPossible, JsonPermissionDenied,
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
        if resource is not None:
            if g.user.id == resource.owner_id:
                return True
            else:
                return False
        else:
                raise ResourceDoesNotExists()


class IsPartner(PermissionBase):
    def has_access(self, resource, **kwargs):
        resource = resource.query.get(kwargs[self.get_resource_id_name(resource)])
        if resource is not None:
            if g.user.id == resource.partner_id:
                return True
            else:
                return False
        else:
            raise ResourceDoesNotExists()


class InPartners(PermissionBase):
    def has_access(self, resource, **kwargs):
        resource = resource.query.get(kwargs[self.get_resource_id_name(resource)])
        if resource is not None:
            if g.user.id in resource.partner_users:
                return True
            else:
                return False
        else:
            raise ResourceDoesNotExists()