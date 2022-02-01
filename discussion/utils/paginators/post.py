from discussion.models.post import Post
from discussion.schemas.post import PostSchema
from discussion.utils.paginators import BasePaginator


class PostPaginator(BasePaginator):

    model = Post
    schema = PostSchema

