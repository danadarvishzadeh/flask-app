
from abc import ABC, abstractmethod

from discussion.utils.errors import ResourceDoesNotExists
from flask import g


class BasePermission(ABC):

    def __init__(self, resource, **kwargs):
        resource = resource.query.get(kwargs[self.get_resource_id_name(resource)])
        if not resource:
            raise ResourceDoesNotExists()
        g.resource = resource

    def get_resource_id_name(resource):
        return resource.__name__.lower() + '_id'

    @abstractmethod
    def has_access(self, resource, **kwargs):
        pass
