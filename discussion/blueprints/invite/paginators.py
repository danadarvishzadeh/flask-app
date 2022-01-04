from discussion.blueprints.invite.schemas import invitation_schema
from discussion.models.invitation import Invitation
from discussion.utils import PaginatorBase


class InvitationPaginator(PaginatorBase):

    model = Invitation
    schema = invitation_schema
