"""autogenerated

Create Date: 2025-04-01 19:15:30.115754

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250401_151526'
down_revision = '20250320_105536'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('file')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('entity_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('entity_field_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('entity_class_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=7), autoincrement=False, nullable=False),
    sa.Column('protocol', sa.VARCHAR(length=5), autoincrement=False, nullable=False),
    sa.Column('namespace', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('path', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('file_format', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('compression_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('size', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upload_client', sa.VARCHAR(length=9), autoincrement=False, nullable=True),
    sa.Column('upload_error', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='pk_file')
    )
    # ### end Alembic commands ###