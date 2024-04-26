import json
from typing import Optional
from collections import defaultdict
import re
from typing import Any

import click
from importers.annotation import AnnotationImporter
from importers.dataset import DatasetImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from importers.frame import FrameImporter
from importers.gain import GainImporter
from importers.key_image import KeyImageImporter
from importers.neuroglancer import NeuroglancerImporter
from importers.rawtilt import RawTiltImporter
from importers.run import RunImporter
from importers.tiltseries import TiltSeriesImporter
from importers.tomogram import TomogramImporter
from importers.voxel_spacing import VoxelSpacingImporter

from common.config import DepositionImportConfig
from common.fs import FileSystemApi

IMPORTERS = [
    AnnotationImporter,
    DatasetKeyPhotoImporter,
    DatasetImporter,
    FrameImporter,
    NeuroglancerImporter,
    TomogramImporter,
    GainImporter,
    KeyImageImporter,
    RawTiltImporter,
    RunImporter,
    TiltSeriesImporter,
    TomogramImporter,
    VoxelSpacingImporter,
]
IMPORTER_DICT = {cls.type_key: cls for cls in IMPORTERS}
IMPORTER_DEP_TREE = {
    DatasetImporter: {
        RunImporter: {
            VoxelSpacingImporter: {
                TomogramImporter: {
                    KeyImageImporter: {},
                    NeuroglancerImporter: {},
                },
                AnnotationImporter: {},
            }, 
            FrameImporter: {
                GainImporter: {},
            },
            TiltSeriesImporter: {},
        },
        DatasetKeyPhotoImporter: {},
    }
}


@click.group()
@click.pass_context
def cli(ctx):
    pass


def common_options(func):
    options = []
    for cls in IMPORTERS:
        plural_key = cls.plural_key.replace("_", "-")
        importer_key = cls.type_key.replace("_", "-")
        options.append(click.option(f"--import-{plural_key}", is_flag=True, default=False))
        options.append(click.option(f"--filter-{importer_key}-name", type=str, default=None, multiple=True))
        options.append(click.option(f"--exclude-{importer_key}-name", type=str, default=None, multiple=True))
        if cls.has_metadata:
            options.append(click.option(f"--import-{importer_key}-metadata", is_flag=True, default=False))
    for option in options:
        func = option(func)
    return func


def flatten_dependency_tree(tree):
    treedict = {}
    for k, v in tree.items():
        treedict[k] = set([])
        treedict[k].update(set(v.keys()))
        for subtype, subdict in flatten_dependency_tree(v).items():
            treedict[subtype] = subdict
            treedict[k].update(subdict)
    return treedict

def do_import(config, tree, to_import, to_iterate, kwargs, parents: Optional[dict[str, Any]] = None):
    if parents is None:
        parents = {}
    for import_class, child_import_classes in tree.items():
        if import_class not in to_iterate:
            print(f"Skipping iteration for {import_class}")
            continue
        print(f"Iterating {import_class}")
        filter_patterns = [re.compile(pattern) for pattern in kwargs.get(f"filter_{import_class.type_key}_name", [])]
        exclude_patterns = [re.compile(pattern) for pattern in kwargs.get(f"exclude_{import_class.type_key}_name", [])]

        parent_args = {}
        for dep in import_class.dependencies:
            parent_args[dep] = parents[dep]

        items = import_class.finder(config, **parent_args)
        for item in items:
            print("found an item!!")
            if list(filter(lambda x: x.match(item.name), exclude_patterns)):
                print(f"Excluding {item.name}..")
                continue
            if filter_patterns and not list(filter(lambda x: x.match(item.name), filter_patterns)):
                print(f"Skipping {item.name}..")
                continue
            if import_class in to_import:
                print(f"Importing {import_class.type_key}")
                # item.import_item()
            if child_import_classes:
                sub_parents = {import_class.type_key: item}
                sub_parents.update(parents)
                do_import(config, child_import_classes, to_import, to_iterate, kwargs, sub_parents)
            # Not all importers have metadata, but we don't expose the option for it unless it's supported
            if kwargs.get(f"import_{import_class.type_key}_metadata"):
                print(f"Importing {import_class.type_key} metadata")
                # item.import_metadata()
        exit()

@cli.command()
@click.argument("config_file", required=True, type=str)
@click.argument("input_bucket", required=True, type=str)
@click.argument("output_path", required=True, type=str)
@click.option("--import-everything", is_flag=True, default=False)
@click.option("--write-mrc/--no-write-mrc", default=True)
@click.option("--write-zarr/--no-write-zarr", default=True)
@click.option("--force-overwrite", is_flag=True, default=False)
@click.option("--local-fs", type=bool, is_flag=True, default=False)
@common_options
@click.pass_context
def convert2(
    ctx,
    config_file: str,
    input_bucket: str,
    output_path: str,
    import_everything: bool,
    force_overwrite: bool,
    local_fs: bool,
    **kwargs,
):
    fs_mode = "s3"
    if local_fs:
        fs_mode = "local"

    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=force_overwrite)

    config = DepositionImportConfig(fs, config_file, output_path, input_bucket, IMPORTERS)
    config.load_map_files()

    iteration_deps = flatten_dependency_tree(IMPORTER_DEP_TREE).items()
    if import_everything:
        to_import = set([k for k in IMPORTERS])
    else:
        to_import = set([k for k in IMPORTERS if kwargs.get(f"import_{k.plural_key}")])
        to_import.update(set([k for k in IMPORTERS if kwargs.get(f"import_{k.type_key}_metadata")]))
    to_iterate = to_import
    to_iterate = to_iterate.union(set([k for k, v in iteration_deps if to_import.intersection(v)]))
    do_import(config, IMPORTER_DEP_TREE, to_import, to_iterate, kwargs)
    exit()


@cli.command()
@click.argument("config_file", required=True, type=str)
@click.argument("input_bucket", required=True, type=str)
@click.argument("output_path", required=True, type=str)
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
@click.option("--filter-dataset-name", type=str, default=None, multiple=True)
@click.option("--filter-run-name", type=str, default=None, multiple=True)
@click.option("--exclude-run-name", type=str, default=None, multiple=True)
@click.option("--make-key-image", type=bool, is_flag=True, default=False)
@click.option("--make-neuroglancer-config", type=bool, is_flag=True, default=False)
@click.option("--write-mrc/--no-write-mrc", default=True)
@click.option("--write-zarr/--no-write-zarr", default=True)
@click.option("--local-fs", type=bool, is_flag=True, default=False)
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
    filter_dataset_name: list[str],
    filter_run_name: list[str],
    exclude_run_name: list[str],
    make_key_image: bool,
    make_neuroglancer_config: bool,
    write_mrc: bool,
    write_zarr: bool,
    local_fs: bool,
):
    fs_mode = "s3"
    if local_fs:
        fs_mode = "local"

    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=force_overwrite)

    config = DepositionImportConfig(fs, config_file, output_path, input_bucket)
    config.load_map_files()

    # Configure which dependencies that do / don't require us to iterate over importer results.
    iterate_tomos = max(
        import_tomograms,
        import_tomogram_metadata,
        import_metadata,
        import_everything,
        make_key_image,
        make_neuroglancer_config,
    )
    iterate_voxelspacings = max(
        iterate_tomos,
        import_annotations,
        import_annotation_metadata,
    )
    iterate_keyimages = max(import_everything, make_key_image)
    iterate_tiltseries = max(import_metadata, import_tiltseries, import_tiltseries_metadata, import_everything)
    iterate_annotations = max(
        import_annotations,
        import_annotation_metadata,
        import_metadata,
        import_everything,
        make_key_image,
    )
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

    exclude_run_name_patterns = [re.compile(pattern) for pattern in exclude_run_name]
    filter_run_name_patterns = [re.compile(pattern) for pattern in filter_run_name]
    filter_ds_name_patterns = [re.compile(pattern) for pattern in filter_dataset_name]
    # Always iterate over datasets and runs.
    datasets = config.find_datasets(DatasetImporter, None, fs)
    for dataset in datasets:
        if filter_dataset_name and not list(filter(lambda x: x.match(dataset.name), filter_ds_name_patterns)):
            print(f"Skipping dataset {dataset.name}..")
            continue
        runs = config.find_runs(RunImporter, dataset, fs)
        for run in runs:
            if list(filter(lambda x: x.match(run.name), exclude_run_name_patterns)):
                print(f"Excluding {run.name}..")
                continue
            if filter_run_name and not list(filter(lambda x: x.match(run.name), filter_run_name_patterns)):
                print(f"Skipping {run.name}..")
                continue
            print(f"Processing {run.name}...")
            if import_run_metadata or import_metadata or import_everything:
                run.import_run_metadata()
            if iterate_voxelspacings:
                voxel_spacings = config.find_voxel_spacings(VoxelSpacingImporter, run, fs)
                for vs in voxel_spacings:
                    if iterate_tomos:
                        tomos = config.find_tomograms(TomogramImporter, vs, fs)
                        for tomo in tomos:
                            if iterate_tomos and not vs.name:
                                vs.set_voxel_spacing(tomo.get_voxel_spacing())
                            if import_tomograms:
                                tomo.import_tomogram(write_mrc=write_mrc, write_zarr=write_zarr)
                            if iterate_keyimages:
                                for keyimage in KeyImageImporter.find_key_images(config, tomo):
                                    keyimage.make_key_image(config)
                            if import_tomogram_metadata:
                                tomo.import_metadata(True)
                            if iterate_ng:
                                for item in NeuroglancerImporter.find_ng(config, tomo):
                                    item.import_neuroglancer()
                    if not iterate_annotations:
                        continue
                    for annotation in AnnotationImporter.find_annotations(config, vs):
                        if import_annotations:
                            print(f"Importing annotation {annotation} ... ")
                            annotation.import_annotations(True)
                        if import_annotation_metadata:
                            print(f"Importing annotation metadata {annotation} ... ")
                            annotation.import_metadata()
            if iterate_frames:
                frame_importers = config.find_frames(FrameImporter, run, fs)
                for frame in frame_importers:
                    frame.import_item()
                gain_importers = config.find_gains(GainImporter, run, fs)
                for gain in gain_importers:
                    gain.import_item()
            if iterate_tiltseries:
                ts_imports = config.find_tiltseries(TiltSeriesImporter, run, fs)
                for importer in ts_imports:
                    if import_tiltseries:
                        importer.import_tiltseries(write_mrc=write_mrc, write_zarr=write_zarr)
                    if import_tiltseries_metadata:
                        importer.import_metadata(True)
                if import_tiltseries:
                    rawtlt_importers = config.find_rawtilts(RawTiltImporter, run, fs)
                    for importer in rawtlt_importers:
                        importer.import_item()
        if import_datasets or import_everything:
            dataset_key_photos_importer = DatasetKeyPhotoImporter.find_dataset_key_photos(config, dataset)
            dataset_key_photos_importer.import_key_photo()
        if import_metadata or import_dataset_metadata or import_everything:
            dataset.import_metadata(output_path)


if __name__ == "__main__":
    cli()
