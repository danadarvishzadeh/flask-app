"""empty message

Revision ID: a0fc03127f13
Revises: 3568586d8b17
Create Date: 2022-01-22 12:03:18.427532

"""
from email.policy import default
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'a0fc03127f13'
down_revision = '3568586d8b17'
branch_labels = None
depends_on = None
from enum import Enum

class StatusEnum(Enum):
    sent = 'Sent'
    accepted = 'Accepted'
    rejected = 'Rejected'


status_enums = postgresql.ENUM(StatusEnum, name='status', values_callable=lambda x: [str(x.value) for x in StatusEnum])


def upgrade():
    status_enums.create(op.get_bind())
    op.alter_column(
        'invitations',
        'status',
        type_=status_enums,
        postgresql_using='status::status',
        server_default='Sent',
    )



def downgrade():
    op.alter_column(
        'invitations',
        'status',
        type_=sa.String(10)
    )
    status_enums.drop(op.get_bind())
