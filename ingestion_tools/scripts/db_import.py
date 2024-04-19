import logging

import boto3
import click
from botocore import UNSIGNED
from botocore.config import Config
from importers.db.annotation import AnnotationAuthorDBImporter, AnnotationDBImporter, StaleAnnotationDeletionDBImporter
from importers.db.base_importer import DBImportConfig
from importers.db.dataset import DatasetAuthorDBImporter, DatasetDBImporter, DatasetFundingDBImporter
from importers.db.run import RunDBImporter, StaleRunDeletionDBImporter
from importers.db.tiltseries import StaleTiltSeriesDeletionDBImporter, TiltSeriesDBImporter
from importers.db.tomogram import StaleTomogramDeletionDBImporter, TomogramAuthorDBImporter, TomogramDBImporter
from importers.db.voxel_spacing import StaleVoxelSpacingDeletionDBImporter, TomogramVoxelSpacingDBImporter

from common import db_models


@click.group()
def cli():
    pass


@cli.command()
@click.argument("s3_bucket", required=True, type=str)
@click.argument("https_prefix", required=True, type=str)
@click.argument("postgres_url", required=True, type=str)
@click.option("--s3_prefix", required=True, default="", type=str)
@click.option(
    "--anonymous",
    is_flag=True,
    required=True,
    default=False,
    type=bool,
    help="Use anonymous access to S3",
)
@click.option(
    "--debug/--no-debug",
    is_flag=True,
    required=True,
    default=False,
    type=bool,
    help="Print DB Queries",
)
@click.option("--filter-dataset", type=str, default=None, multiple=True)
@click.option("--import-annotations", is_flag=True, default=False)
@click.option("--import-annotation-authors", is_flag=True, default=False)
@click.option("--import-dataset-authors", is_flag=True, default=False)
@click.option("--import-dataset-funding", is_flag=True, default=False)
@click.option("--import-runs", is_flag=True, default=False)
@click.option("--import-tiltseries", is_flag=True, default=False)
@click.option("--import-tomograms", is_flag=True, default=False)
@click.option("--import-tomogram-authors", is_flag=True, default=False)
@click.option("--import-tomogram-voxel-spacing", is_flag=True, default=False)
@click.option("--import-everything", is_flag=True, default=False)
@click.option("--endpoint-url", type=str, default=None)
def load(
    s3_bucket: str,
    https_prefix: str,
    postgres_url: str,
    s3_prefix: str,
    anonymous: bool,
    debug: bool,
    filter_dataset: list[str],
    import_annotations: bool,
    import_annotation_authors: bool,
    import_dataset_authors: bool,
    import_dataset_funding: bool,
    import_runs: bool,
    import_tiltseries: bool,
    import_tomograms: bool,
    import_tomogram_authors: bool,
    import_tomogram_voxel_spacing: bool,
    import_everything: bool,
    endpoint_url: str,
):
    db_models.db.init(postgres_url)
    if debug:
        logger = logging.getLogger("peewee")
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

    if import_everything:
        import_annotations = True
        import_annotation_authors = True
        import_dataset_authors = True
        import_dataset_funding = True
        import_runs = True
        import_tiltseries = True
        import_tomograms = True
        import_tomogram_authors = True
        import_tomogram_voxel_spacing = True
    else:
        import_annotations = max(import_annotations, import_annotation_authors)
        import_tomograms = max(import_tomograms, import_tomogram_authors)
        import_tomogram_voxel_spacing = max(import_annotations, import_tomograms, import_tomogram_voxel_spacing)
        import_runs = max(import_runs, import_tiltseries, import_tomogram_voxel_spacing)

    s3_config = Config(signature_version=UNSIGNED) if anonymous else None
    s3_client = boto3.client("s3", endpoint_url=endpoint_url, config=s3_config)
    config = DBImportConfig(s3_client, s3_bucket, https_prefix)
    for dataset in DatasetDBImporter.get_items(config, s3_prefix):
        if filter_dataset and dataset.dir_prefix not in filter_dataset:
            print(f"Skipping {dataset.dir_prefix}...")
            continue

        dataset_obj = dataset.import_to_db()
        dataset_id = dataset_obj.id

        if import_dataset_authors:
            dataset_authors = DatasetAuthorDBImporter.get_item(dataset_id, dataset, config)
            dataset_authors.import_to_db()

        if import_dataset_funding:
            funding = DatasetFundingDBImporter.get_item(dataset_id, dataset, config)
            funding.import_to_db()

        if not import_runs:
            continue

        run_cleaner = StaleRunDeletionDBImporter(dataset_id, config)
        for run in RunDBImporter.get_item(dataset_id, dataset, config):
            print(f"Processing Run with prefix {run.dir_prefix}")
            run_obj = run.import_to_db()
            run_id = run_obj.id
            run_cleaner.mark_as_active(run_obj)

            if import_tiltseries:
                tiltseries_cleaner = StaleTiltSeriesDeletionDBImporter(run_id, config)
                tiltseries = TiltSeriesDBImporter.get_item(run_id, run, config)
                if tiltseries:
                    tiltseries_obj = tiltseries.import_to_db()
                    tiltseries_cleaner.mark_as_active(tiltseries_obj)
                tiltseries_cleaner.remove_stale_objects()

            if not import_tomogram_voxel_spacing:
                continue

            voxel_spacing_cleaner = StaleVoxelSpacingDeletionDBImporter(run_id, config)
            for voxel_spacing in TomogramVoxelSpacingDBImporter.get_items(run_id, run, config):
                voxel_spacing_obj = voxel_spacing.import_to_db()

                if import_tomograms:
                    tomogram_cleaner = StaleTomogramDeletionDBImporter(voxel_spacing_obj.id, config)
                    for tomogram in TomogramDBImporter.get_item(voxel_spacing_obj.id, voxel_spacing, config):
                        tomogram_obj = tomogram.import_to_db()
                        tomogram_cleaner.mark_as_active(tomogram_obj)

                        if import_tomogram_authors:
                            tomogram_authors = TomogramAuthorDBImporter.get_item(tomogram_obj.id, tomogram, config)
                            tomogram_authors.import_to_db()
                    tomogram_cleaner.remove_stale_objects()

                if import_annotations:
                    annotation_cleaner = StaleAnnotationDeletionDBImporter(voxel_spacing_obj.id, config)
                    for annotation in AnnotationDBImporter.get_item(voxel_spacing_obj.id, voxel_spacing, config):
                        annotation_obj = annotation.import_to_db()
                        annotation_cleaner.mark_as_active(annotation_obj)

                        if import_annotation_authors:
                            annotation_authors = AnnotationAuthorDBImporter.get_item(
                                annotation_obj.id,
                                annotation,
                                config,
                            )
                            annotation_authors.import_to_db()
                    annotation_cleaner.remove_stale_objects()

                voxel_spacing_cleaner.mark_as_active(voxel_spacing_obj)

            voxel_spacing_cleaner.remove_stale_objects()

        run_cleaner.remove_stale_objects()


if __name__ == "__main__":
    cli()
