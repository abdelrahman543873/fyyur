"""empty message

Revision ID: e44df6d46f16
Revises: 330215d8bf41
Create Date: 2020-11-21 10:09:22.710868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e44df6d46f16'
down_revision = '330215d8bf41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.String(), nullable=True))
    op.add_column('Artist', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_talent')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###