import logging
import os

import boto3
import click
from botocore import UNSIGNED
from botocore.config import Config
from s3fs import S3FileSystem

from db_import.common.config import DBImportConfig
from db_import.importers.alignment import AlignmentImporter, PerSectionAlignmentParametersImporter
from db_import.importers.annotation import (
    AnnotationAuthorImporter,
    AnnotationFileImporter,
    AnnotationImporter,
    AnnotationMethodLinkImporter,
    AnnotationShapeImporter,
)
from db_import.importers.dataset import DatasetAuthorDBImporter, DatasetDBImporter, DatasetFundingDBImporter
from db_import.importers.deposition import DepositionAuthorDBImporter, DepositionDBImporter, DepositionTypeDBImporter
from db_import.importers.frame import FrameImporter
from db_import.importers.frame_acquisition_file import FrameAcquisitionFileImporter
from db_import.importers.gain import GainImporter
from db_import.importers.run import RunDBImporter, StaleRunDeletionDBImporter
from db_import.importers.tiltseries import (
    PerSectionParametersImporter,
    StaleTiltSeriesDeletionDBImporter,
    TiltSeriesDBImporter,
)
from db_import.importers.tomogram import TomogramAuthorImporter, TomogramImporter
from db_import.importers.voxel_spacing import StaleVoxelSpacingDeletionDBImporter, TomogramVoxelSpacingDBImporter
from platformics.database.connect import init_sync_db

logger = logging.getLogger("db_import")
logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    pass


def db_import_options(func):
    options = []
    options.append(click.option("--import-annotations", is_flag=True, default=False))
    options.append(click.option("--import-annotation-authors", is_flag=True, default=False))
    options.append(click.option("--import-annotation-method-links", is_flag=True, default=False))
    options.append(click.option("--import-dataset-authors", is_flag=True, default=False))
    options.append(click.option("--import-dataset-funding", is_flag=True, default=False))
    options.append(click.option("--import-depositions", is_flag=True, default=False))
    options.append(click.option("--import-runs", is_flag=True, default=False))
    options.append(click.option("--import-alignments", is_flag=True, default=False))
    options.append(click.option("--import-gains", is_flag=True, default=False))
    options.append(click.option("--import-frames", is_flag=True, default=False))
    options.append(click.option("--import-frame-acquisition-files", is_flag=True, default=False))
    options.append(click.option("--import-tiltseries", is_flag=True, default=False))
    options.append(click.option("--import-tomograms", is_flag=True, default=False))
    options.append(click.option("--import-tomogram-authors", is_flag=True, default=False))
    options.append(click.option("--import-tomogram-voxel-spacing", is_flag=True, default=False))
    options.append(click.option("--import-everything", is_flag=True, default=False))
    options.append(click.option("--deposition-id", type=str, default=None, multiple=True))
    options.append(
        click.option(
            "--anonymous",
            is_flag=True,
            required=True,
            default=False,
            type=bool,
            help="Use anonymous access to S3",
        ),
    )
    for option in options:
        func = option(func)
    return func


@cli.command()
@click.argument("s3_bucket", required=True, type=str)
@click.argument("https_prefix", required=True, type=str)
@click.option("--postgres_url", required=False, type=str)
@click.option("--filter-dataset", type=str, default=None, multiple=True)
@click.option("--s3-prefix", required=True, default="", type=str)
@click.option("--endpoint-url", type=str, default=None)
@click.option("--debug", is_flag=True, default=False)
@db_import_options
def load(
    s3_bucket: str,
    https_prefix: str,
    postgres_url: str,
    s3_prefix: str,
    anonymous: bool,
    filter_dataset: list[str],
    import_annotations: bool,
    import_annotation_authors: bool,
    import_annotation_method_links: bool,
    import_dataset_authors: bool,
    import_dataset_funding: bool,
    import_depositions: bool,
    import_runs: bool,
    import_alignments: bool,
    import_gains: bool,
    import_frames: bool,
    import_frame_acquisition_files: bool,
    import_tiltseries: bool,
    import_tomograms: bool,
    import_tomogram_authors: bool,
    import_tomogram_voxel_spacing: bool,
    import_everything: bool,
    deposition_id: list[str],
    endpoint_url: str,
    debug: bool,  # Just included for compatibility with the old script.
):
    load_func(
        s3_bucket,
        https_prefix,
        postgres_url,
        s3_prefix,
        anonymous,
        filter_dataset,
        import_annotations,
        import_annotation_authors,
        import_annotation_method_links,
        import_dataset_authors,
        import_dataset_funding,
        import_depositions,
        import_runs,
        import_alignments,
        import_gains,
        import_frames,
        import_frame_acquisition_files,
        import_tiltseries,
        import_tomograms,
        import_tomogram_authors,
        import_tomogram_voxel_spacing,
        import_everything,
        deposition_id,
        endpoint_url,
    )


def load_func(
    s3_bucket: str,
    https_prefix: str,
    postgres_url: str | None = None,
    s3_prefix: str | None = None,
    anonymous: bool = False,
    filter_dataset: list[str] | None = None,
    import_annotations: bool = False,
    import_annotation_authors: bool = False,
    import_annotation_method_links: bool = False,
    import_dataset_authors: bool = False,
    import_dataset_funding: bool = False,
    import_depositions: bool = False,
    import_runs: bool = False,
    import_alignments: bool = False,
    import_gains: bool = False,
    import_frames: bool = False,
    import_frame_acquisition_files: bool = False,
    import_tiltseries: bool = False,
    import_tomograms: bool = False,
    import_tomogram_authors: bool = False,
    import_tomogram_voxel_spacing: bool = False,
    import_everything: bool = False,
    deposition_id: list[str] | None = None,
    endpoint_url: str | None = None,
):
    if not postgres_url:
        postgres_url = f"postgresql+psycopg://{os.environ['PLATFORMICS_DATABASE_USER']}:{os.environ['PLATFORMICS_DATABASE_PASSWORD']}@{os.environ['PLATFORMICS_DATABASE_HOST']}:{os.environ['PLATFORMICS_DATABASE_PORT']}/{os.environ['PLATFORMICS_DATABASE_NAME']}"
    db = init_sync_db(postgres_url)
    session = db.session()

    if import_everything:
        import_annotations = True
        import_annotation_authors = True
        import_annotation_method_links = True
        import_dataset_authors = True
        import_dataset_funding = True
        import_depositions = True
        import_runs = True
        import_alignments = True
        import_gains = True
        import_frame_acquisition_files = True
        import_frames = True
        import_tiltseries = True
        import_tomograms = True
        import_tomogram_authors = True
        import_tomogram_voxel_spacing = True
    else:
        import_annotations = max(import_annotations, import_annotation_authors, import_annotation_method_links)
        import_tomograms = max(import_tomograms, import_tomogram_authors)
        import_tomogram_voxel_spacing = max(import_annotations, import_tomograms, import_tomogram_voxel_spacing)
        import_tiltseries = max(import_tiltseries, import_alignments)
        import_frame_acquisition_files = max(import_frames, import_frame_acquisition_files)
        import_runs = max(
            import_runs,
            import_alignments,
            import_gains,
            import_frame_acquisition_files,
            import_tiltseries,
            import_tomogram_voxel_spacing,
        )

    s3_config = Config(signature_version=UNSIGNED) if anonymous else None
    s3_client = boto3.client("s3", endpoint_url=endpoint_url, config=s3_config)
    s3fs = S3FileSystem(client_kwargs={"endpoint_url": endpoint_url})
    config = DBImportConfig(s3_client, s3fs, s3_bucket, https_prefix, session)

    if import_depositions and deposition_id:
        for dep_id in deposition_id:
            for deposition_importer in DepositionDBImporter.get_items(config, dep_id):
                deposition_obj = deposition_importer.import_to_db()
                deposition_authors = DepositionAuthorDBImporter.get_item(deposition_obj.id, deposition_importer, config)
                deposition_authors.import_to_db()
                deposition_types = DepositionTypeDBImporter.get_item(deposition_obj.id, deposition_importer, config)
                deposition_types.import_to_db()

    config.load_deposition_map()

    for dataset in DatasetDBImporter.get_items(config, s3_prefix):
        if filter_dataset and dataset.dir_prefix not in filter_dataset:
            logger.info("Skipping %s...", dataset.dir_prefix)
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
            logger.info("Processing Run with prefix %s", run.dir_prefix)
            run_obj = run.import_to_db()
            run_id = run_obj.id
            run_cleaner.mark_as_active(run_obj)

            parents = {"run": run_obj, "dataset": dataset_obj}
            if import_frame_acquisition_files:
                frame_acquisition_file_importer = FrameAcquisitionFileImporter(config, **parents)
                for _ in frame_acquisition_file_importer.import_items():
                    if import_frames:
                        frame_importer = FrameImporter(config, **parents)
                        frame_importer.import_items()
            if import_gains:
                gain_importer = GainImporter(config, **parents)
                gain_importer.import_items()
            if import_tiltseries:
                tiltseries_cleaner = StaleTiltSeriesDeletionDBImporter(run_id, config)
                tiltseries = TiltSeriesDBImporter.get_item(run_id, run, config)
                if tiltseries:
                    tiltseries_obj = tiltseries.import_to_db()
                    tiltseries_cleaner.mark_as_active(tiltseries_obj)
                    # import per section parameters
                    metadata_file_path = tiltseries.get_metadata_file_path()
                    parents["tiltseries"] = tiltseries_obj
                    per_section_parameters_importer = PerSectionParametersImporter(
                        config,
                        metadata_file_path,
                        **parents,
                    )
                    per_section_parameters_importer.import_items()
                    parents.pop("tiltseries")
                tiltseries_cleaner.remove_stale_objects()
            if import_alignments:
                alignment_importer = AlignmentImporter(config, **parents)
                for alignment_obj in alignment_importer.import_items():
                    parents = {"run": run_obj, "alignment": alignment_obj}
                    per_section_alignment_parameters_importer = PerSectionAlignmentParametersImporter(
                        config,
                        **parents,
                    )
                    per_section_alignment_parameters_importer.import_items()

            if not import_tomogram_voxel_spacing:
                continue

            voxel_spacing_cleaner = StaleVoxelSpacingDeletionDBImporter(run_id, config)
            for voxel_spacing in TomogramVoxelSpacingDBImporter.get_items(run_id, run, config):
                voxel_spacing_obj = voxel_spacing.import_to_db()

                if import_tomograms:
                    parents = {"run": run_obj, "voxel_spacing": voxel_spacing_obj}
                    tomo_importer = TomogramImporter(config, **parents)
                    for tomogram_obj in tomo_importer.import_items():
                        if import_tomogram_authors:
                            parents = {"run": run_obj, "voxel_spacing": voxel_spacing_obj, "tomogram": tomogram_obj}
                            tomogram_authors = TomogramAuthorImporter(config, **parents)
                            tomogram_authors.import_items()

                if import_annotations:
                    parents = {"tomogram_voxel_spacing": voxel_spacing_obj, "run": run_obj, "dataset": dataset_obj}
                    anno_importer = AnnotationImporter(config, **parents)
                    for anno in anno_importer.import_items():
                        parents["annotation"] = anno
                        annoshape = AnnotationShapeImporter(config, **parents)
                        for shape in annoshape.import_items():
                            annofile = AnnotationFileImporter(config, annotation_shape=shape, **parents)
                            annofile.import_items()

                        if import_annotation_authors:
                            authors = AnnotationAuthorImporter(config, **parents)
                            authors.import_items()
                        if import_annotation_method_links:
                            methodlinks = AnnotationMethodLinkImporter(config, **parents)
                            methodlinks.import_items()

                voxel_spacing_cleaner.mark_as_active(voxel_spacing_obj)

            voxel_spacing_cleaner.remove_stale_objects()

        run_cleaner.remove_stale_objects()
        session.commit()
    session.commit()


if __name__ == "__main__":
    cli()
