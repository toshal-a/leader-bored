"""empty message

Revision ID: 0e2c55c870fe
Revises: 7859cb880184
Create Date: 2020-07-14 02:41:18.697187

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0e2c55c870fe'
down_revision = '7859cb880184'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contests')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contests',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('contest_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('starting_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('duration_seconds', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('contest_type', postgresql.ENUM('CF', 'IOI', 'ICPC', name='contest_types'), server_default=sa.text("'CF'::contest_types"), autoincrement=False, nullable=False),
    sa.Column('added_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('reverted_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_added', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_contests')
    )
    # ### end Alembic commands ###
