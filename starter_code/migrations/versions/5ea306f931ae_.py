"""empty message

Revision ID: 5ea306f931ae
Revises: 5ecbb46edee3
Create Date: 2020-11-18 10:23:39.405131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ea306f931ae'
down_revision = '5ecbb46edee3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('venue_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'Show', 'Venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_column('Show', 'venue_id')
    # ### end Alembic commands ###
