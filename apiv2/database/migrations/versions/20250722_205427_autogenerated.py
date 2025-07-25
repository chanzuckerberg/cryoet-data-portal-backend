"""autogenerated

Create Date: 2025-07-23 03:54:29.904500

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20250722_205427"
down_revision = "20250320_105536"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("dataset", sa.Column("assay_label", sa.String(), nullable=True))
    op.add_column("dataset", sa.Column("assay_ontology_id", sa.String(), nullable=True))
    op.add_column("dataset", sa.Column("development_stage_name", sa.String(), nullable=True))
    op.add_column("dataset", sa.Column("development_stage_ontology_id", sa.String(), nullable=True))
    op.add_column("dataset", sa.Column("disease_name", sa.String(), nullable=True))
    op.add_column("dataset", sa.Column("disease_ontology_id", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("dataset", "disease_ontology_id")
    op.drop_column("dataset", "disease_name")
    op.drop_column("dataset", "development_stage_ontology_id")
    op.drop_column("dataset", "development_stage_name")
    op.drop_column("dataset", "assay_ontology_id")
    op.drop_column("dataset", "assay_label")
    # ### end Alembic commands ###
