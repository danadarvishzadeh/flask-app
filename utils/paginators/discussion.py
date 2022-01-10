
from discussion.models.discussion import Discussion
from discussion.schemas.discussion import discussion_schema
from discussion.utils.paginators.base_paginator import PaginatorBase


class DiscussionPaginator(PaginatorBase):

    model = Discussion
    schema = discussion_schema
