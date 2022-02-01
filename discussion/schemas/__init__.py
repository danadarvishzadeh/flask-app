from marshmallow import Schema
from .discussion import *
from .user import *
from .invitation import *
from .post import *


class PaginationSchema(Schema):
    page = Integer()