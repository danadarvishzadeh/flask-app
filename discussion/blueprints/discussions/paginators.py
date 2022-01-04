from discussion.models.discussion import Discussion
from discussion.utils import PaginatorBase
from discussion.blueprints.discussions.schemas import discussion_schema


class DiscussionPaginator(PaginatorBase):

    model = Discussion
    schema = discussion_schema