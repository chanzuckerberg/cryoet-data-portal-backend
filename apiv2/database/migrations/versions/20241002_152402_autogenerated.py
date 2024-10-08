"""autogenerated

Create Date: 2024-10-02 19:24:04.875030

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20241002_152402"
down_revision = "20240918_121738"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "frame_acquisition_file",
        sa.Column("run_id", sa.Integer(), nullable=True),
        sa.Column("s3_mdoc_path", sa.String(), nullable=False),
        sa.Column("https_mdoc_path", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["run.id"], name=op.f("fk_frame_acquisition_file_run_id_run")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_frame_acquisition_file")),
    )
    op.create_index(op.f("ix_frame_acquisition_file_id"), "frame_acquisition_file", ["id"], unique=False)
    op.create_index(op.f("ix_frame_acquisition_file_run_id"), "frame_acquisition_file", ["run_id"], unique=False)
    op.create_table(
        "gain_file",
        sa.Column("run_id", sa.Integer(), nullable=True),
        sa.Column("s3_file_path", sa.String(), nullable=False),
        sa.Column("https_file_path", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["run.id"], name=op.f("fk_gain_file_run_id_run")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_gain_file")),
    )
    op.create_index(op.f("ix_gain_file_id"), "gain_file", ["id"], unique=False)
    op.create_index(op.f("ix_gain_file_run_id"), "gain_file", ["run_id"], unique=False)
    op.create_table(
        "annotation_method_link",
        sa.Column("annotation_id", sa.Integer(), nullable=True),
        sa.Column(
            "link_type",
            sa.Enum(
                "documentation",
                "models_weights",
                "other",
                "source_code",
                "website",
                name="annotation_method_link_type_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("link", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["annotation_id"],
            ["annotation.id"],
            name=op.f("fk_annotation_method_link_annotation_id_annotation"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_annotation_method_link")),
    )
    op.create_index(
        op.f("ix_annotation_method_link_annotation_id"),
        "annotation_method_link",
        ["annotation_id"],
        unique=False,
    )
    op.create_index(op.f("ix_annotation_method_link_id"), "annotation_method_link", ["id"], unique=False)
    op.drop_index("ix_per_section_parameters_frame_id", table_name="per_section_parameters")
    op.drop_index("ix_per_section_parameters_id", table_name="per_section_parameters")
    op.drop_index("ix_per_section_parameters_tiltseries_id", table_name="per_section_parameters")
    op.drop_table("per_section_parameters")
    op.add_column(
        "alignment",
        sa.Column(
            "alignment_method",
            sa.Enum(
                "projection_matching",
                "patch_tracking",
                "fiducial_based",
                name="alignment_method_type_enum",
                native_enum=False,
            ),
            nullable=True,
        ),
    )
    op.add_column("alignment", sa.Column("s3_alignment_metadata", sa.String(), nullable=True))
    op.add_column("alignment", sa.Column("https_alignment_metadata", sa.String(), nullable=True))
    op.add_column("alignment", sa.Column("is_portal_standard", sa.Boolean(), nullable=True))
    op.drop_column("alignment", "local_alignment_file")
    op.drop_column("annotation", "method_links")
    op.add_column("per_section_alignment_parameters", sa.Column("volume_x_rotation", sa.Float(), nullable=True))
    op.drop_column("per_section_alignment_parameters", "in_plane_rotation")
    op.add_column(
        "per_section_alignment_parameters",
        sa.Column("in_plane_rotation", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.drop_column("per_section_alignment_parameters", "beam_tilt")
    op.drop_column("tiltseries", "https_gain_file")
    op.drop_column("tiltseries", "frames_count")
    op.drop_column("tiltseries", "https_collection_metadata")
    op.drop_column("tiltseries", "s3_collection_metadata")
    op.drop_column("tiltseries", "s3_gain_file")
    op.drop_column("tomogram", "is_canonical")
    op.add_column("tomogram", sa.Column("is_portal_standard", sa.Boolean(), nullable=True))
    op.add_column("tomogram", sa.Column("is_author_submitted", sa.Boolean(), nullable=True))
    op.add_column("tomogram", sa.Column("is_visualization_default", sa.Boolean(), nullable=True))
    op.add_column("tomogram", sa.Column("publications", sa.String(), nullable=True))
    op.add_column("tomogram", sa.Column("related_database_entries", sa.String(), nullable=True))
    op.add_column("tomogram", sa.Column("deposition_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tomogram", sa.Column("release_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tomogram", sa.Column("last_modified_date", sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("tomogram", sa.Column("is_canonical", sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column("tomogram", "last_modified_date")
    op.drop_column("tomogram", "release_date")
    op.drop_column("tomogram", "deposition_date")
    op.drop_column("tomogram", "related_database_entries")
    op.drop_column("tomogram", "publications")
    op.drop_column("tomogram", "is_visualization_default")
    op.drop_column("tomogram", "is_author_submitted")
    op.drop_column("tomogram", "is_portal_standard")
    op.add_column("tiltseries", sa.Column("s3_gain_file", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column("tiltseries", sa.Column("s3_collection_metadata", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(
        "tiltseries",
        sa.Column("https_collection_metadata", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column("tiltseries", sa.Column("frames_count", sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column("tiltseries", sa.Column("https_gain_file", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column(
        "per_section_alignment_parameters",
        sa.Column("beam_tilt", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    )
    op.drop_column("per_section_alignment_parameters", "in_plane_rotation")
    op.add_column(
        "per_section_alignment_parameters",
        sa.Column("in_plane_rotation", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    )
    op.drop_column("per_section_alignment_parameters", "volume_x_rotation")
    op.add_column("annotation", sa.Column("method_links", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column("alignment", sa.Column("local_alignment_file", sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column("alignment", "is_portal_standard")
    op.drop_column("alignment", "https_alignment_metadata")
    op.drop_column("alignment", "s3_alignment_metadata")
    op.drop_column("alignment", "alignment_method")
    op.create_table(
        "per_section_parameters",
        sa.Column("frame_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("tiltseries_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("z_index", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("defocus", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
        sa.Column("astigmatism", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
        sa.Column("astigmatic_angle", sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["frame_id"], ["frame.id"], name="fk_per_section_parameters_frame_id_frame"),
        sa.ForeignKeyConstraint(
            ["tiltseries_id"],
            ["tiltseries.id"],
            name="fk_per_section_parameters_tiltseries_id_tiltseries",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_per_section_parameters"),
    )
    op.create_index(
        "ix_per_section_parameters_tiltseries_id",
        "per_section_parameters",
        ["tiltseries_id"],
        unique=False,
    )
    op.create_index("ix_per_section_parameters_id", "per_section_parameters", ["id"], unique=False)
    op.create_index("ix_per_section_parameters_frame_id", "per_section_parameters", ["frame_id"], unique=False)
    op.drop_index(op.f("ix_annotation_method_link_id"), table_name="annotation_method_link")
    op.drop_index(op.f("ix_annotation_method_link_annotation_id"), table_name="annotation_method_link")
    op.drop_table("annotation_method_link")
    op.drop_index(op.f("ix_gain_file_run_id"), table_name="gain_file")
    op.drop_index(op.f("ix_gain_file_id"), table_name="gain_file")
    op.drop_table("gain_file")
    op.drop_index(op.f("ix_frame_acquisition_file_run_id"), table_name="frame_acquisition_file")
    op.drop_index(op.f("ix_frame_acquisition_file_id"), table_name="frame_acquisition_file")
    op.drop_table("frame_acquisition_file")
    # ### end Alembic commands ###