# Checks for empty columns in a v2 database.
import os

import click
import sqlalchemy as sa
from database import models
from platformics.database.connect import init_sync_db

# Seems ok, but could stand to doublecheck:
# Tomogram.processing_software has all null values! (mapped)
# Annotation.object_state has all null values! (mapped)
# Annotation.confidence_precision has all null values! (mapped)
# Annotation.confidence_recall has all null values! (mapped)
# Annotation.ground_truth_used has all null values! (mapped)
# Dataset.tissue_name has all null values! (mapped)
# Dataset.tissue_id has all null values! (mapped)
# Dataset.cell_name has all null values! (mapped)
# Dataset.cell_type_id has all null values! (mapped)
# Dataset.other_setup has all null values! (mapped)
# Dataset.cell_component_name has all null values! (mapped)
# Dataset.cell_component_id has all null values! (mapped)
# Tiltseries.microscope_phase_plate has all null values! (mapped)
# Tiltseries.microscope_image_corrector has all null values! (mapped)
# Tiltseries.microscope_additional_info has all null values! (mapped)
# Tiltseries.aligned_tiltseries_binning has all null values! (mapped)


def model_class_cols(model_cls):
    inspected = sa.inspect(model_cls)
    cols = {item: inspected.columns[item.key].type for item in inspected.mapper.column_attrs}
    return cols


def check_table(model_cls):
    # AnnotationFile.source is TODO - we need to populate it somehow.
    expected_to_be_empty = [
        "TomogramAuthor.email",
        "TomogramAuthor.affiliation_name",
        "TomogramAuthor.affiliation_address",
        "TomogramAuthor.affiliation_identifier",
        "DatasetAuthor.email",
        "DatasetAuthor.affiliation_name",
        "DatasetAuthor.affiliation_address",
        "DatasetAuthor.affiliation_identifier",
        "DepositionAuthor.email",
        "DepositionAuthor.affiliation_name",
        "DepositionAuthor.affiliation_address",
        "DepositionAuthor.affiliation_identifier",
        "AnnotationAuthor.email",
        "AnnotationAuthor.affiliation_name",
        "AnnotationAuthor.affiliation_address",
        "AnnotationAuthor.affiliation_identifier",
        "Frame.raw_angle",
        "Frame.acquisition_order",
        "Frame.dose",
        "Frame.is_gain_corrected",
        # These are just not being populated yet.
        "Deposition.key_photo_url",
        "Deposition.key_photo_thumbnail_url",
        # Needs s3 ingestion feedback:
        "Tomogram.deposition_date",
        "Tomogram.release_date",
        "Tomogram.last_modified_date",
        "Tomogram.publications",
        "Tomogram.related_database_entries",
        "Tomogram.neuroglancer_config",
    ]
    db = init_sync_db(
        f"postgresql+psycopg://{os.environ['PLATFORMICS_DATABASE_USER']}:{os.environ['PLATFORMICS_DATABASE_PASSWORD']}@{os.environ['PLATFORMICS_DATABASE_HOST']}:{os.environ['PLATFORMICS_DATABASE_PORT']}/{os.environ['PLATFORMICS_DATABASE_NAME']}",
    )
    with db.session() as session:
        # print(f"processing {model_cls}")
        for col, col_type in model_class_cols(model_cls).items():
            rows = session.scalars(
                sa.select(sa.func.count(model_cls.id)).where(getattr(model_cls, col.key) != None),  # noqa
            ).one()
            if not rows and str(col) not in expected_to_be_empty:
                print(f"column {col} has all null values!")
                continue
            if col_type in (sa.Integer, sa.Float, sa.Numeric):
                rows = session.scalars(
                    sa.select(sa.func.count(model_cls.id)).where(getattr(model_cls, col.key) != 0),
                ).one()
                if not rows:
                    print(f"column {col} has all 0 values!")
                    continue
            if col_type in (sa.String, sa.Text):
                rows = session.scalars(
                    sa.select(sa.func.count(model_cls.id)).where(getattr(model_cls, col.key) != ""),
                ).one()
                if not rows:
                    print(f"column {col} has all empty-string values!")
                    continue


@click.command()
def check_tables():
    model_list = [
        models.Alignment,
        models.Annotation,
        models.AnnotationAuthor,
        models.AnnotationFile,
        models.AnnotationMethodLink,
        models.AnnotationShape,
        models.Dataset,
        models.DatasetAuthor,
        models.DatasetFunding,
        models.Deposition,
        models.DepositionAuthor,
        models.DepositionType,
        models.Frame,
        models.GainFile,
        models.Run,
        models.Tiltseries,
        models.Tomogram,
        models.TomogramAuthor,
        models.TomogramVoxelSpacing,
    ]

    for model in model_list:
        check_table(model)


if __name__ == "__main__":
    check_tables()
