import re
from typing import Any, Optional

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
                AnnotationImporter: {},
                TomogramImporter: {
                    KeyImageImporter: {},
                    NeuroglancerImporter: {},
                },
            },
            FrameImporter: {
                GainImporter: {},
            },
            TiltSeriesImporter: {},
            RawTiltImporter: {},
        },
        DatasetKeyPhotoImporter: {},
    },
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
        treedict[k] = set()
        treedict[k].update(set(v.keys()))
        for subtype, subdict in flatten_dependency_tree(v).items():
            treedict[subtype] = subdict
            treedict[k].update(subdict)
    return treedict


def do_import(config, tree, to_import, metadata_import, to_iterate, kwargs, parents: Optional[dict[str, Any]] = None):
    parents = dict(parents) if parents else {}
    for import_class, child_import_classes in tree.items():
        if import_class not in to_iterate:
            continue
        filter_patterns = [re.compile(pattern) for pattern in kwargs.get(f"filter_{import_class.type_key}_name", [])]
        exclude_patterns = [re.compile(pattern) for pattern in kwargs.get(f"exclude_{import_class.type_key}_name", [])]

        # It's probably clearer to send a flat dict of parents instead of
        # requiring importers to recurse through a single parent to find
        # all ancestors
        parent_args = dict(parents)

        items = import_class.finder(config, **parent_args)
        for item in items:
            if list(filter(lambda x: x.match(item.name), exclude_patterns)):
                print(f"Excluding {item.name}..")
                continue
            if filter_patterns and not list(filter(lambda x: x.match(item.name), filter_patterns)):
                print(f"Skipping {item.name}..")
                continue
            if import_class in to_import:
                print(f"Importing {import_class.type_key} {item.name}")
                item.import_item()
            if child_import_classes:
                sub_parents = {import_class.type_key: item}
                sub_parents.update(parents)
                do_import(config, child_import_classes, metadata_import, to_import, to_iterate, kwargs, sub_parents)
            # Not all importers have metadata, but we don't expose the option for it unless it's supported
            if import_class in metadata_import and item.has_metadata:
                print(f"Importing {import_class.type_key} metadata")
                item.import_metadata()


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
def convert(
    ctx,
    config_file: str,
    input_bucket: str,
    output_path: str,
    import_everything: bool,
    write_mrc: bool,
    write_zarr: bool,
    force_overwrite: bool,
    local_fs: bool,
    **kwargs,
):
    fs_mode = "s3"
    if local_fs:
        fs_mode = "local"

    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=force_overwrite)

    config = DepositionImportConfig(fs, config_file, output_path, input_bucket, IMPORTERS)
    config.write_mrc = write_mrc
    config.write_zarr = write_zarr
    config.load_map_files()

    iteration_deps = flatten_dependency_tree(IMPORTER_DEP_TREE).items()
    if import_everything:
        to_import = set(IMPORTERS)
        metadata_import = set(IMPORTERS)
        to_iterate = set(IMPORTERS)
    else:
        to_import = {k for k in IMPORTERS if kwargs.get(f"import_{k.plural_key}")}
        metadata_import = {k for k in IMPORTERS if kwargs.get(f"import_{k.type_key}_metadata")}
        needs_iteration = to_import.union(metadata_import)
        to_iterate = needs_iteration.union({k for k, v in iteration_deps if needs_iteration.intersection(v)})
    do_import(config, IMPORTER_DEP_TREE, to_import, metadata_import, to_iterate, kwargs)
    exit()


if __name__ == "__main__":
    cli()
