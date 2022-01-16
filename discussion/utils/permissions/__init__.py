
from abc import ABC, abstractmethod

from discussion.utils.errors import ResourceDoesNotExists
from flask import g


class BasePermission(ABC):

    def __init__(self, **kwargs):
        model = kwargs.get('resource')
        self.resource = model.query.get(kwargs[self.get_resource_id_name(model)])
        if not self.resource:
            raise ResourceDoesNotExists()
        store_resource = kwargs.get('store_resource')
        if store_resource:
            g.resource = self.resource

    def get_resource_id_name(self, model):
        return model.__name__.lower() + '_id'

    @abstractmethod
    def has_access(self):
        pass
