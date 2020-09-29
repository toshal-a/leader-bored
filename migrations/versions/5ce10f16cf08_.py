"""empty message

Revision ID: 5ce10f16cf08
Revises: 0e2c55c870fe
Create Date: 2020-08-09 23:10:22.108621

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ce10f16cf08'
down_revision = '0e2c55c870fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usercodeforcesmonth',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('month', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('avg_percentile', sa.Float(), nullable=True),
    sa.Column('aggr_percentile', sa.Float(), nullable=True),
    sa.Column('contests_played', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_usercodeforcesmonth_user_id_users')),
    sa.PrimaryKeyConstraint('user_id', 'month', 'year', name=op.f('pk_usercodeforcesmonth'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('usercodeforcesmonth')
    # ### end Alembic commands ###