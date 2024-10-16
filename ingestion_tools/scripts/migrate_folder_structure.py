import json
import os.path
import re
import urllib.parse
from typing import Any, Optional

import click as click
from importers.alignment import AlignmentImporter
from importers.base_importer import BaseImporter
from importers.utils import IMPORTER_DEP_TREE, IMPORTERS
from standardize_dirs import flatten_dependency_tree

from common.config import DepositionImportConfig
from common.formats import tojson
from common.fs import FileSystemApi

OLD_PATHS = {
    "alignment": "{dataset_name}/{run_name}/TiltSeries/",
    # "alignment_metadata": "{dataset_name}/{run_name}/Alignments/{alignment_id}-alignment_metadata.json",
    "annotation": "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/Annotations",
    "annotation_metadata": "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/Annotations/*.json",
    "annotation_viz": (
        "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/NeuroglancerPrecompute/{annotation_id}-*"
    ),
    "collection_metadata": "{dataset_name}/{run_name}/TiltSeries/",
    "dataset": "{dataset_name}",
    "dataset_keyphoto": "{dataset_name}/Images",
    "dataset_metadata": "{dataset_name}/dataset_metadata.json",
    "deposition": "depositions_metadata/{deposition_name}",
    "deposition_keyphoto": "depositions_metadata/{deposition_name}/Images",
    "deposition_metadata": "depositions_metadata/{deposition_name}/deposition_metadata.json",
    "frame": "{dataset_name}/{run_name}/Frames",
    "gain": "{dataset_name}/{run_name}/Frames/",
    "key_image": "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/KeyPhotos/",
    "rawtilt": "{dataset_name}/{run_name}/TiltSeries",
    "run": "{dataset_name}/{run_name}",
    "run_metadata": "{dataset_name}/{run_name}/run_metadata.json",
    "tiltseries": "{dataset_name}/{run_name}/TiltSeries",
    "tiltseries_metadata": "{dataset_name}/{run_name}/TiltSeries/tiltseries_metadata.json",
    "tomogram": "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/CanonicalTomogram",
    "tomogram_metadata": "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/CanonicalTomogram/"
                         "tomogram_metadata.json",
    "viz_config": "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/CanonicalTomogram/"
                  "neuroglancer_config.json",
    "voxel_spacing": "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}",
}


def move(config: DepositionImportConfig, old_path: str, new_path: str):
    if config.fs.exists(old_path):
        print(f"Moving {old_path} to {new_path}")
        config.fs.move(old_path, new_path, recursive=True)
    else:
        print(f"Skipping move of {old_path} as it does not exist")


def delete(config: DepositionImportConfig, path: str):
    print(f"Deleting {path}")
    if hasattr(config.fs, "s3fs"):
        config.fs.s3fs.rm(path)


def migrate_volume(
        cls, config: DepositionImportConfig, parents: dict[str, Any], kwargs,
) -> None:
    """
    Moves the volumes of the entity to include the identifier in the path (default of 100)
    Moves the metadata of the entity  to include the identifier in the path (default of 100)
    :param cls:
    :param config:
    :param parents:
    :param kwargs:
    :param migrate_metadata:
    :return:
    """
    output_path = cls.get_output_path()
    metadata_path = kwargs.get("metadata_path")
    metadata_dir = os.path.dirname(metadata_path)
    for fmt, key in {"mrc": "mrc_files", "zarr": "omezarr_dir"}.items():
        filename = cls.metadata.get(key)
        if isinstance(filename, list):
            filename = filename[0]
        old_path = os.path.join(metadata_dir, filename)
        new_path = f"{output_path}.{fmt}"
        move(config, old_path, new_path)
    if kwargs.get("migrate_metadata", True):
        move(config, metadata_path, cls.get_metadata_path())


def migrate_tomograms(cls, config: DepositionImportConfig, parents: dict[str, Any], kwargs) -> None:
    """
    Moves the tomograms in the run to include the identifier in the path (default of 100)
    Moves the tomogram_metadata in the run to include the identifier in the path (default of 100)
    Update the path to Reconstruction/VoxelSpacingXX.XX/Tomograms/...

    Update the tomogram path in the metadata json
    Update the key_photos file path in the metadata json
    Update the neuroglancer_config path name in the metadata json
    :param cls:
    :param config:
    :param parents:
    :param kwargs:
    :return:
    """
    migrate_volume(cls, config, parents, {**kwargs, "migrate_metadata": False})
    # This is a very hacky way to get the metadata path set up with the correct values
    cls.allow_imports = True
    cls.import_metadata()
    delete(config, kwargs.get("metadata_path"))


def migrate_viz_config(cls, config: DepositionImportConfig, parents: dict[str, Any], kwargs) -> None:
    """
    Renames the neuroglancer_config in the run to include the identifier (default of 100)
    Updates the path of the neuroglancer_config.json to Reconstruction/VoxelSpacingXX.XX/NeuroglancerPrecompute
    Update the path to the layer in the neuroglancer_config.json
    :param cls:
    :param config:
    :param parents:
    :param kwargs:
    :return:
    """
    old_path = cls.path
    new_path = cls.get_output_path()
    with config.fs.open(old_path, "r") as f:
        ng_config = json.load(f)
    if image_layer := next((layer for layer in ng_config["layers"] if layer["type"] == "image"), None):
        path = cls.parents["tomogram"].get_output_path().replace(config.output_prefix, "") + ".zarr"
        image_url = urllib.parse.urljoin("https://files.cryoetdataportal.cziscience.com", path)
        image_layer["source"]["url"] = "zarr://" + image_url

    old_precompute_path = cls.parents["voxel_spacing"].get_output_path().replace(config.output_prefix, "")
    new_precompute_path = old_precompute_path.replace("Tomogram", "Reconstruction")
    for layer in ng_config["layers"]:
        if layer["type"] in {"annotation", "segmentation"}:
            url = layer["source"]["url"]
            layer["source"]["url"] = url.replace(old_precompute_path, new_precompute_path)
    with config.fs.open(new_path, "w") as f:
        f.write(tojson(ng_config))

    delete(config, old_path)


def migrate_key_image(cls, config: DepositionImportConfig, parents: dict[str, Any], kwargs) -> None:
    """
    Renames the key photo in the run to include the identifier (default of 100)
    Update the path to Reconstruction/VoxelSpacingXX.XX/KeyPhotos/..
    :param cls:
    :param config:
    :param parents:
    :param kwargs:
    :return:
    """
    old_path = cls.path
    file_name = f"{os.path.basename(old_path)}"
    new_path = os.path.join(cls.get_output_path(), file_name)
    move(config, old_path, new_path)


def migrate_alignments(cls, config: DepositionImportConfig, parents: dict[str, Any], kwargs) -> None:
    for old_path in cls.file_paths.values():
        new_path = os.path.join(cls.get_output_path(), os.path.basename(old_path).lstrip(f"{cls.identifier}-"))
        move(config, old_path, new_path)
    metadata_path = kwargs.get("metadata_path")
    if metadata_path:
        move(config, metadata_path, cls.get_metadata_path())


def migrate_annotations(cls, config: DepositionImportConfig, parents: dict[str, Any], kwargs) -> None:
    """
    Moves the annotations in the run to the Reconstruction path
    Moves the annotation_metadata in the run to the Reconstruction path
    :param cls:
    :param config:
    :param parents:
    :param kwargs:
    :return:
    """
    output_path = cls.get_output_path()
    metadata_path = kwargs.get("metadata_path")
    for file in cls.metadata["files"]:
        filename = file["path"]
        shape = file["shape"].lower()
        old_path = os.path.join(config.output_prefix, filename)
        new_path = f"{output_path}_{shape}{os.path.splitext(filename)[1]}"
        file["path"] = new_path.replace(config.output_prefix, "").lstrip("/")
        move(config, old_path, new_path)
    cls.metadata["alignment_metadata_path"] = cls.local_metadata["alignment_metadata_path"]

    path = f"{cls.get_output_path()}.json"
    print(f"Writing metadata to {path}")
    with config.fs.open(path, "w") as f:
        f.write(tojson(cls.metadata))

    delete(config, metadata_path)


def migrate_files(cls, config: DepositionImportConfig, parents: dict[str, Any], kwargs) -> None:
    dir_name = os.path.basename(cls.path)
    old_path = cls.path
    new_path = os.path.join(cls.get_output_path(), dir_name)
    move(config, old_path, new_path)


MIGRATION_MAP = {
    "alignment": migrate_alignments,
    "annotation": migrate_annotations,
    "annotation_viz": migrate_files,
    "collection_metadata": migrate_files,
    "gain": migrate_files,
    "key_image": migrate_key_image,
    "rawtilt": migrate_files,
    "tiltseries": migrate_volume,
    "tomogram": migrate_tomograms,
    "viz_config": migrate_viz_config,
}


@click.group()
@click.pass_context
def cli(ctx):
    pass


def migrate_common_options(func):
    options = []
    for cls in IMPORTERS:
        plural_key = cls.plural_key.replace("_", "-")
        importer_key = cls.type_key.replace("_", "-")
        options.append(click.option(f"--migrate-{plural_key}", is_flag=True, default=False))
        options.append(click.option(f"--filter-{importer_key}-name", type=str, default=None, multiple=True))
        options.append(click.option(f"--exclude-{importer_key}-name", type=str, default=None, multiple=True))
    for option in options:
        func = option(func)
    return func


def _get_glob_vars(migrate_cls: BaseImporter, parents: dict[str, Any]) -> dict[str, Any]:
    glob_vars = {f"{migrate_cls.type_key}_name": "*", f"{migrate_cls.type_key}_id": "*"}
    if parents:
        for parent in parents.values():
            glob_vars.update(parent.get_glob_vars())
    return glob_vars


def finder(migrate_cls, config: DepositionImportConfig, **parents: dict[str, BaseImporter]):
    if migrate_cls.type_key in {"deposition", "dataset", "dataset_keyphoto", "deposition_keyphoto"}:
        # Uses the default finders as ingestion for these entities
        finder_configs = config.get_object_configs(migrate_cls.type_key)
        for _finder in finder_configs:
            sources = _finder.get("sources", [])
            for source in sources:
                source_finder_factory = migrate_cls.finder_factory(source, migrate_cls)
                for item in source_finder_factory.find(config, {}, **parents):
                    item.allow_imports = False
                    yield item, {}
    elif f"{migrate_cls.type_key}_metadata" in OLD_PATHS:
        # Glob the metadata to define the entity
        print(f"Finding metadata for {migrate_cls.type_key}..")
        glob_vars = _get_glob_vars(migrate_cls, parents)
        glob_str = OLD_PATHS.get(f"{migrate_cls.type_key}_metadata").format(**glob_vars)
        glob_path = os.path.join(config.output_prefix, glob_str)
        for file_path in config.fs.glob(glob_path):
            args = {"metadata_path": file_path}
            with config.fs.open(file_path, "r") as f:
                metadata = json.load(f)
            kwargs = {
                "allow_imports": False,
                "parents": parents,
                "config": config,
                "metadata": metadata,
            }
            if migrate_cls.type_key in {"annotation", "tomogram"}:
                glob_vars = {**_get_glob_vars(migrate_cls, parents), **{"alignment_id": "100"}}
                alignment_path = AlignmentImporter.dir_path.format(**glob_vars)
                kwargs["alignment_metadata_path"] = os.path.join(alignment_path, "alignment_metadata.json")
            if migrate_cls.type_key == "annotation":
                name = re.search(re.compile(glob_str.replace("*", "(.*)")), file_path).group(1)
                additional_args = {
                    "identifier": int(name.split("-")[0]),
                    "name": name,
                    "path": os.path.join(config.output_prefix, metadata["files"][0]["path"]),
                }
                yield migrate_cls(**{**kwargs, **additional_args}), args
            elif migrate_cls.type_key == "run":
                name = re.search(re.compile(glob_str.replace("*", "(.*)")), file_path).group(1)
                yield migrate_cls(name=name, path=file_path, **kwargs), args
            else:
                name, path, results = migrate_cls.get_name_and_path(metadata, None, file_path, {})
                kwargs["name"] = name
                if path:
                    kwargs["path"] = path
                elif results:
                    kwargs["file_paths"] = results
                yield migrate_cls(**kwargs), args
    elif migrate_cls.type_key in OLD_PATHS and migrate_cls.type_key not in {"frame"}:
        finder_configs = []
        for configs in config.get_object_configs(migrate_cls.type_key):
            for source in configs.get("sources", []):
                if "source_multi_glob" in source:
                    finder_configs.extend(source.get("source_multi_glob").get("list_globs"))
                elif "source_glob" in source:
                    finder_configs.append(source.get("source_glob").get("list_glob"))
                elif "literal" in source:
                    literal_values = source.get("literal").get("value")
                    if not isinstance(literal_values, list):
                        literal_values = [literal_values]
                    finder_configs.append(literal_values)
        for source_glob in finder_configs:
            dest_suffix = None
            if migrate_cls.type_key == "gain" and source_glob.endswith(".dm4"):
                dest_suffix = "*.mrc"
            if migrate_cls.type_key == "key_image":
                dest_suffix = "*.png"
            elif isinstance(source_glob, str):
                dest_suffix = f"*{os.path.splitext(source_glob)[1]}"
            elif migrate_cls.type_key == "alignment" and isinstance(source_glob, list):
                print("Skipping alignment migration as source is a literal")
                continue
            path = OLD_PATHS.get(f"{migrate_cls.type_key}").format(**_get_glob_vars(migrate_cls, parents))
            glob = os.path.join(path, dest_suffix) if dest_suffix else path
            source = {
                "destination_glob": {
                    "list_glob": os.path.join(config.output_prefix, glob),
                    "name_regex": "VoxelSpacing(.*)" if migrate_cls.type_key == "voxel_spacing" else "(.*)",
                    "match_regex": "(.*)",
                },
            }
            importer_factory = migrate_cls.finder_factory(source, migrate_cls)
            for item in importer_factory.find(config, {}, **parents):
                yield item, {}
    return []


def _migrate(config, tree, to_migrate, to_iterate, kwargs, parents: Optional[dict[str, Any]] = None):
    parents = dict(parents) if parents else {}
    for import_class, child_import_classes in tree.items():
        if import_class not in to_iterate:
            continue
        filter_patterns = [re.compile(pattern) for pattern in kwargs.get(f"filter_{import_class.type_key}_name", [])]
        exclude_patterns = [re.compile(pattern) for pattern in kwargs.get(f"exclude_{import_class.type_key}_name", [])]

        parent_args = dict(parents)

        for item, args in finder(import_class, config, **parent_args):
            print(f"Iterating {item.type_key}: {item.name}")
            if list(filter(lambda x: x.match(item.name), exclude_patterns)):
                print(f"Excluding {item.name}..")
                continue
            if filter_patterns and not list(filter(lambda x: x.match(item.name), filter_patterns)):
                print(f"Skipping {item.name}..")
                continue

            if child_import_classes:
                sub_parents = {import_class.type_key: item}
                sub_parents.update(parents)
                _migrate(config, child_import_classes, to_migrate, to_iterate, kwargs, sub_parents)

            type_key = item.type_key
            if import_class in to_migrate and type_key in MIGRATION_MAP:
                if OLD_PATHS.get(type_key, "").rstrip("/") == item.dir_path:
                    print(f"Skipping {type_key} migration as old path and new path are same")
                else:
                    print(f"Migrating {type_key} {item.name}")
                    MIGRATION_MAP.get(type_key)(item, config, parents, args)


@cli.command()
@click.argument("config_file", required=True, type=str)
@click.argument("output_bucket", required=True, type=str)
@click.option("--migrate-everything", is_flag=True, default=False)
@click.option("--local-fs", type=bool, is_flag=True, default=False)
@migrate_common_options
@click.pass_context
def migrate(
    ctx,
    config_file: str,
    output_bucket: str,
    migrate_everything: bool,
    local_fs: bool,
    **kwargs,
):
    fs_mode = "s3"
    if local_fs:
        fs_mode = "local"
    # The increased read timeout prevents failures for the large files.
    fs = FileSystemApi.get_fs_api(mode=fs_mode, force_overwrite=False, config_kwargs={"read_timeout": 40})
    config = DepositionImportConfig(fs, config_file, output_bucket, output_bucket, IMPORTERS)
    # config.load_map_files()

    iteration_deps = flatten_dependency_tree(IMPORTER_DEP_TREE).items()
    if migrate_everything:
        to_migrate = set(IMPORTERS)
        to_iterate = set(IMPORTERS)
    else:
        to_migrate = {k for k in IMPORTERS if kwargs.get(f"migrate_{k.plural_key}")}
        to_iterate = to_migrate.union({k for k, v in iteration_deps if to_migrate.intersection(v)})
    _migrate(config, IMPORTER_DEP_TREE, to_migrate, to_iterate, kwargs)


if __name__ == "__main__":
    cli()
