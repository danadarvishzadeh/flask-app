from discussion.models.discussion import Discussion
from discussion.utils.paginator import PaginatorBase
from discussion.schemas.discussion import discussion_schema


class DiscussionPaginator(PaginatorBase):

    model = Discussion
    schema = discussion_schema