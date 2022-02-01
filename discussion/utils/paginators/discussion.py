
from discussion.models.discussion import Discussion
from discussion.schemas.discussion import DiscussionSchema
from discussion.utils.paginators import BasePaginator


class DiscussionPaginator(BasePaginator):

    model = Discussion
    schema = DiscussionSchema
