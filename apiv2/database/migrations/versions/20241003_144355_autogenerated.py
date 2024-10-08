"""autogenerated

Create Date: 2024-10-03 18:43:58.750446

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20241003_144355"
down_revision = "20241002_152402"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("frame", "https_gain_file")
    op.drop_column("frame", "s3_gain_file")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("frame", sa.Column("s3_gain_file", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column("frame", sa.Column("https_gain_file", sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
