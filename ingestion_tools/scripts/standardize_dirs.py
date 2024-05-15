import os
import os.path
import re

import click
from importers.annotation import AnnotationImporter
from importers.dataset import DatasetImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from importers.frames import FramesImporter
from importers.key_image import KeyImageImporter
from importers.neuroglancer import NeuroglancerImporter
from importers.run import RunImporter
from importers.tiltseries import RawTiltImporter, TiltSeriesImporter
from importers.tomogram import TomogramImporter

from common.config import DataImportConfig
from common.fs import FileSystemApi


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.argument("config_file", required=True, type=str)
@click.argument("input_bucket", required=True, type=str)
@click.argument("output_path", required=True, type=str)
@click.option("--force-overwrite", is_flag=True, default=False)
@click.option("--import-tomograms", is_flag=True, default=False)
@click.option("--import-tomogram-metadata", is_flag=True, default=False)
@click.option("--import-annotations", is_flag=True, default=False)
@click.option("--import-annotation-metadata", is_flag=True, default=False)
@click.option("--import-metadata", is_flag=True, default=False)
@click.option("--import-frames", is_flag=True, default=False)
@click.option("--import-tiltseries", is_flag=True, default=False)
@click.option("--import-tiltseries-metadata", is_flag=True, default=False)
@click.option("--import-run-metadata", is_flag=True, default=False)
@click.option("--import-datasets", is_flag=True, default=False)
@click.option("--import-dataset-metadata", is_flag=True, default=False)
@click.option("--import-everything", is_flag=True, default=False)
@click.option("--filter-run-name", type=str, default=None, multiple=True)
@click.option("--exclude-run-name", type=str, default=None, multiple=True)
@click.option("--make-key-image", type=bool, is_flag=True, default=False)
@click.option("--make-neuroglancer-config", type=bool, is_flag=True, default=False)
@click.option("--import-neuroglancer-precompute", type=bool, is_flag=True, default=False)
@click.option("--write-mrc/--no-write-mrc", default=True)
@click.option("--write-zarr/--no-write-zarr", default=True)
@click.option("--local_fs", type=bool, is_flag=True, default=False)
@click.pass_context
def convert(
    ctx,
    config_file: str,
    input_bucket: str,
    output_path: str,
    force_overwrite: bool,
    import_tomograms: bool,
    import_tomogram_metadata: bool,
    import_annotations: bool,
    import_annotation_metadata: bool,
    import_metadata: bool,
    import_frames: bool,
    import_tiltseries: bool,
    import_tiltseries_metadata: bool,
    import_run_metadata: bool,
    import_datasets: bool,
    import_dataset_metadata: bool,
    import_everything: bool,
    filter_run_name: list[str],
    exclude_run_name: list[str],
    make_key_image: bool,
    make_neuroglancer_config: bool,
    import_neuroglancer_precompute: bool,
    write_mrc: bool,
    write_zarr: bool,
    local_fs: bool,
):
    fs_mode = "s3"
    if local_fs:
        fs_mode = "local"

    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=force_overwrite)

    config = DataImportConfig(fs, config_file, output_path, input_bucket)
    os.makedirs(os.path.join(output_path, config.destination_prefix), exist_ok=True)
    config.load_map_files()

    # Configure which dependencies that do / don't require us to iterate over importer results.
    iterate_annotations = max(
        import_annotations,
        import_annotation_metadata,
        import_metadata,
        import_neuroglancer_precompute,
        make_key_image,
    )
    iterate_tomos = max(
        import_tomograms,
        import_tomogram_metadata,
        import_metadata,
        import_everything,
        make_key_image,
        make_neuroglancer_config,
        iterate_annotations,
    )
    iterate_keyimages = max(import_everything, make_key_image)
    iterate_tiltseries = max(import_metadata, import_tiltseries, import_tiltseries_metadata, import_everything)
    iterate_frames = max(import_frames, import_everything)
    iterate_ng = max(make_neuroglancer_config, import_everything)
    if import_everything:
        import_tomograms = True
        import_tomogram_metadata = True
        import_annotations = True
        import_annotation_metadata = True
        import_tiltseries = True
        import_tiltseries_metadata = True
        import_datasets = True
        import_dataset_metadata = True
        import_neuroglancer_precompute = True
        make_neuroglancer_config = True
        make_key_image = True

    exclude_run_name_patterns = [re.compile(pattern) for pattern in exclude_run_name]
    filter_run_name_patterns = [re.compile(pattern) for pattern in filter_run_name]
    # Always iterate over datasets and runs.
    dataset = DatasetImporter(config, None)
    for run in RunImporter.find_runs(config, dataset):
        if list(filter(lambda x: x.match(run.run_name), exclude_run_name_patterns)):
            print(f"Excluding {run.run_name}..")
            continue
        if filter_run_name and not list(filter(lambda x: x.match(run.run_name), filter_run_name_patterns)):
            print(f"Skipping {run.run_name}..")
            continue
        print(f"Processing {run.run_name}...")
        if import_run_metadata or import_metadata or import_everything:
            run.import_run_metadata()
        if iterate_tomos:
            for tomo in TomogramImporter.find_tomograms(config, run):
                if iterate_tomos and not run.voxel_spacing:
                    run.set_voxel_spacing(tomo.get_voxel_spacing())
                if import_tomograms:
                    tomo.import_tomogram(write_mrc=write_mrc, write_zarr=write_zarr)
                annotations = []
                if iterate_annotations:
                    annotations = AnnotationImporter.find_annotations(config, tomo)
                    for annotation in annotations:
                        if import_annotations:
                            annotation.import_annotations(write_mrc=write_mrc, write_zarr=write_zarr)
                        if import_annotation_metadata:
                            annotation.import_metadata()
                        if import_neuroglancer_precompute:
                            annotation.import_neuroglancer_component()
                if iterate_keyimages:
                    for keyimage in KeyImageImporter.find_key_images(config, tomo):
                        keyimage.make_key_image(config)
                if import_tomogram_metadata:
                    tomo.import_metadata(True)
                if iterate_ng:
                    for item in NeuroglancerImporter.find_ng(config, tomo):
                        item.import_neuroglancer(annotations)
        if iterate_frames:
            frame_imports = FramesImporter.find_frames(config, run)
            for importer in frame_imports:
                importer.import_frames()
        if iterate_tiltseries:
            ts_imports = TiltSeriesImporter.find_tiltseries(config, run)
            for importer in ts_imports:
                if import_tiltseries:
                    importer.import_tiltseries(write_mrc=write_mrc, write_zarr=write_zarr)
                if import_tiltseries_metadata:
                    importer.import_metadata(True)
            if import_tiltseries:
                raw_imports = RawTiltImporter.find_rawtilts(config, run)
                for importer in raw_imports:
                    importer.import_rawtilts()
    if import_datasets or import_everything:
        dataset_key_photos_importer = DatasetKeyPhotoImporter.find_dataset_key_photos(config, dataset)
        dataset_key_photos_importer.import_key_photo()
    if import_metadata or import_dataset_metadata or import_everything:
        dataset.import_metadata(output_path)


if __name__ == "__main__":
    cli()
