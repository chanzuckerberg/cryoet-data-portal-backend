import click
import logging

from common import db_models
from importers.db_base_importer import DBImportConfig
from importers.db_dataset import DatasetDBImporter, DatasetFundingDBImporter, DatasetAuthorDBImporter


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

    config = DBImportConfig(anonymous, s3_bucket, https_prefix)
    for dataset in DatasetDBImporter.get_items(config, s3_prefix):
        if filter_dataset and dataset.dir_prefix not in filter_dataset:
            print(f"Skipping {dataset.dir_prefix}...")
            continue

        dataset_obj = dataset.import_to_db()
        
        if import_dataset_authors:
            dataset_authors = DatasetAuthorDBImporter.get_item(dataset_obj.id, dataset, config)
            dataset_authors.import_to_db()

        if import_dataset_funding:
            funding = DatasetFundingDBImporter.get_item(dataset_obj.id, dataset, config)
            funding.import_to_db()


if __name__ == "__main__":
    cli()
