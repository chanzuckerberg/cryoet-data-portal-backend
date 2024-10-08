"""autogenerated

Create Date: 2024-09-18 16:17:41.833870

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20240918_121738"
down_revision = "20240926_161943"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("deposition", "deposition_description", new_column_name="description")
    op.alter_column("deposition", "deposition_title", new_column_name="title")
    op.alter_column("deposition", "publications", new_column_name="deposition_publications")
    op.alter_column("dataset", "publications", new_column_name="dataset_publications")
    op.alter_column("tiltseries", "tiltseries_frames_count", new_column_name="frames_count")
    op.add_column("deposition", sa.Column("key_photo_url", sa.String(), nullable=True))
    op.add_column("deposition", sa.Column("key_photo_thumbnail_url", sa.String(), nullable=True))
    op.alter_column(
        "tiltseries",
        "acceleration_voltage",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "tiltseries",
        "aligned_tiltseries_binning",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Integer(),
        existing_nullable=True,
    )
    op.alter_column(
        "tomogram",
        "size_x",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "tomogram",
        "size_y",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "tomogram",
        "size_z",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.add_column("annotation", sa.Column("method_links", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "tiltseries",
        "aligned_tiltseries_binning",
        existing_type=sa.Integer(),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=True,
    )
    op.alter_column(
        "tiltseries",
        "acceleration_voltage",
        existing_type=sa.Integer(),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )
    op.alter_column("deposition", "description", new_column_name="deposition_description")
    op.alter_column("deposition", "title", new_column_name="deposition_title")
    op.alter_column("deposition", "deposition_publications", new_column_name="publications")
    op.alter_column("tiltseries", "frames_count", new_column_name="tiltseries_frames_count")
    op.alter_column("dataset", "dataset_publications", new_column_name="publications")
    op.drop_column("deposition", "key_photo_thumbnail_url")
    op.drop_column("deposition", "key_photo_url")
    op.alter_column(
        "tomogram",
        "size_z",
        existing_type=sa.Integer(),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )
    op.alter_column(
        "tomogram",
        "size_y",
        existing_type=sa.Integer(),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )
    op.alter_column(
        "tomogram",
        "size_x",
        existing_type=sa.Integer(),
        type_=sa.DOUBLE_PRECISION(precision=53),
        existing_nullable=False,
    )
    op.drop_column("annotation", "method_links")
    # ### end Alembic commands ###
