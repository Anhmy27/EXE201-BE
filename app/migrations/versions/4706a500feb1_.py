"""empty message

Revision ID: 4706a500feb1
Revises: 0456cd22aac1
Create Date: 2025-06-01 18:15:18.503681

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4706a500feb1'
down_revision = '0456cd22aac1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('home_work', sa.Column('description', sa.Text(collation='utf8mb4_unicode_ci'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('home_work', 'description')
    # ### end Alembic commands ###
