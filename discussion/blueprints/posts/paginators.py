from discussion.schemas.post import post_schema
from discussion.models.post import Post
from discussion.utils.paginator import PaginatorBase


class PostPaginator(PaginatorBase):

    model = Post
    schema = post_schema