"""Add google auth

Revision ID: 75e8a7ed4c18
Revises: a5182c75ae87
Create Date: 2023-04-19 21:45:38.832409

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '75e8a7ed4c18'
down_revision = 'a5182c75ae87'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('google_id', sa.String(length=250), nullable=True))
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=250),
               nullable=True)
        # batch_op.create_unique_constraint("unique_id", ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        # batch_op.drop_constraint("unique_id", type_='unique')
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=250),
               nullable=False)
        batch_op.drop_column('google_id')
    # ### end Alembic commands ###