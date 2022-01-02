"""adding constraint

Revision ID: 05af1f62c474
Revises: 9f87de40681c
Create Date: 2022-01-02 11:37:38.601812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05af1f62c474'
down_revision = '9f87de40681c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('unique_invitation', 'invitation', ['inviter_id', 'invited_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_invitation', 'invitation', type_='unique')
    # ### end Alembic commands ###
