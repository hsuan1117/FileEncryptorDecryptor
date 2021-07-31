"""empty message

Revision ID: 0a73263d81e4
Revises: 
Create Date: 2021-07-31 15:41:43.480214

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a73263d81e4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('device',
    sa.Column('uid', sa.Text(), nullable=False),
    sa.Column('key', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('uid'),
    sa.UniqueConstraint('key')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('device')
    # ### end Alembic commands ###
