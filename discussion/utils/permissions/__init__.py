
from abc import ABC, abstractmethod

from discussion.utils.errors import ResourceDoesNotExists
from flask import g


class BasePermission(ABC):

    def __init__(self, model, store_resource=True):
        self.resource = model.query.get(kwargs[self.get_resource_id_name(model)])
        if not resource:
            raise ResourceDoesNotExists()
        if store_resource:
            g.resource = resource

    def get_resource_id_name(model):
        return model.__name__.lower() + '_id'

    @abstractmethod
    def has_access(self):
        pass
