"""autogenerated

Create Date: 2025-02-12 19:41:44.724662

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '20250212_144142'
down_revision = '20250117_170249'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('annotation_author', sa.Column('kaggle_id', sa.String(), nullable=True))
    op.add_column('dataset_author', sa.Column('kaggle_id', sa.String(), nullable=True))
    op.add_column('deposition', sa.Column('tag', sa.String(), nullable=True))
    op.add_column('deposition_author', sa.Column('kaggle_id', sa.String(), nullable=True))
    op.add_column('tomogram_author', sa.Column('kaggle_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tomogram_author', 'kaggle_id')
    op.drop_column('deposition_author', 'kaggle_id')
    op.drop_column('deposition', 'tag')
    op.drop_column('dataset_author', 'kaggle_id')
    op.drop_column('annotation_author', 'kaggle_id')
    # ### end Alembic commands ###
