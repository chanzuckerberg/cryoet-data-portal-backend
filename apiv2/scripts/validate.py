# Checks for empty columns in a v2 database.
import os

import click
import sqlalchemy as sa
from database import models

from platformics.database.connect import init_sync_db


def model_class_cols(model_cls):
    inspected = sa.inspect(model_cls)
    cols = {item: inspected.columns[item.key].type for item in inspected.mapper.column_attrs}
    return cols


def check_table(model_cls):
    # AnnotationFile.source is TODO - we need to populate it somehow.
    expected_to_be_empty = [
        "Alignment.alignment_type",
        "Alignment.volume_x_offset",
        "Alignment.volume_y_offset",
        "Alignment.volume_z_offset",
        "Alignment.x_rotation_offset",
        "Alignment.tilt_offset",
        "Alignment.local_alignment_file",
        "AnnotationAuthor.email",
        "AnnotationAuthor.affiliation_name",
        "AnnotationAuthor.affiliation_address",
        "AnnotationAuthor.affiliation_identifier",
        "Dataset.tissue_name",
        "Dataset.tissue_id",
        "DatasetAuthor.email",
        "DatasetAuthor.affiliation_name",
        "DatasetAuthor.affiliation_address",
        "DatasetAuthor.affiliation_identifier",
        "DepositionAuthor.email",
        "DepositionAuthor.affiliation_name",
        "DepositionAuthor.affiliation_address",
        "DepositionAuthor.affiliation_identifier",
        "Tiltseries.microscope_image_corrector",
        "Tiltseries.s3_gain_file",
        "Tiltseries.https_gain_file",
        "TomogramAuthor.email",
        "TomogramAuthor.affiliation_name",
        "TomogramAuthor.affiliation_address",
        "TomogramAuthor.affiliation_identifier",
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
        models.AnnotationShape,
        models.Dataset,
        models.DatasetAuthor,
        models.DatasetFunding,
        models.Deposition,
        models.DepositionAuthor,
        models.DepositionType,
        # models.Frame,
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
