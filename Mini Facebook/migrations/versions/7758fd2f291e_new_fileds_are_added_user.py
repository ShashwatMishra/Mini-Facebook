"""new fileds are added user

Revision ID: 7758fd2f291e
Revises: 5444eea98e3f
Create Date: 2019-05-03 01:12:53.120773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7758fd2f291e'
down_revision = '5444eea98e3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('country', sa.String(), nullable=True))
    op.add_column('user', sa.Column('gender', sa.String(), nullable=True))
    op.add_column('user', sa.Column('relationship_status', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'relationship_status')
    op.drop_column('user', 'gender')
    op.drop_column('user', 'country')
    # ### end Alembic commands ###
