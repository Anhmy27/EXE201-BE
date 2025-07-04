"""empty message

Revision ID: 557b8192f6c5
Revises: 4706a500feb1
Create Date: 2025-06-02 00:57:42.079018

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '557b8192f6c5'
down_revision = '4706a500feb1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_do_home_work',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.String(length=50), nullable=True),
    sa.Column('home_work_id', sa.String(length=50), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('score', mysql.INTEGER(unsigned=True), nullable=True),
    sa.Column('created_date', mysql.INTEGER(unsigned=True), nullable=True),
    sa.Column('modified_date', mysql.INTEGER(unsigned=True), nullable=True),
    sa.ForeignKeyConstraint(['home_work_id'], ['home_work.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_do_home_work_created_date'), 'user_do_home_work', ['created_date'], unique=False)
    op.add_column('user_answer', sa.Column('user_do_home_work_id', sa.String(length=50), nullable=True))
    op.create_foreign_key(None, 'user_answer', 'user_do_home_work', ['user_do_home_work_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user_answer', type_='foreignkey')
    op.drop_column('user_answer', 'user_do_home_work_id')
    op.drop_index(op.f('ix_user_do_home_work_created_date'), table_name='user_do_home_work')
    op.drop_table('user_do_home_work')
    # ### end Alembic commands ###
