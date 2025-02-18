import contextlib
import csv
import os
import os.path
import re
from copy import deepcopy
from typing import TYPE_CHECKING, Any

import yaml

from common.fs import FileSystemApi

if TYPE_CHECKING:
    from importers.base_importer import BaseImporter
else:
    BaseImporter = "BaseImporter"


class RunOverride:
    run_regex: re.Pattern[str]
    tiltseries: dict[str, Any] | None
    tomograms: dict[str, Any] | None

    def __init__(self, run_regex: re.Pattern[str], tiltseries: dict[str, Any] | None, tomograms: dict[str, Any] | None):
        self.run_regex = run_regex
        self.tiltseries = tiltseries
        self.tomograms = tomograms


class DepositionImportConfig:
    https_prefix = os.getenv("DOMAIN_NAME", "https://files.cryoetdataportal.cziscience.com")
    # Core metadata
    source_prefix: str

    output_prefix: str
    fs: FileSystemApi
    tomo_format: str
    tomo_key_photo_glob: str | None = None
    tomo_voxel_size: str
    # Override handling
    overrides: list[dict[str, Any]] | None = None
    # Override configuration
    run_to_tomo_map_file: str | None = None
    run_to_tomo_map: dict[str, str] | None = None
    run_to_frame_map_csv: str | None = None
    run_to_frame_map: dict[str, str] | None = None
    run_to_ts_map_csv: str | None = None
    run_to_ts_map: dict[str, str] | None = None
    rawtilt_files: list[str] | None = None
    run_data_map: dict[str, Any]
    run_data_map_file: str | None = None

    # Stash the configs we handle for each type of object we support
    object_configs: dict[str, Any] | None = None

    def __init__(
        self,
        fs: FileSystemApi,
        config_path: str,
        output_prefix: str,
        input_bucket: str,
        object_classes: list[BaseImporter],
    ):
        self.output_prefix = output_prefix
        self.fs = fs
        self.run_to_tomo_map = {}
        self.run_data_map = {}
        self.run_to_frame_map = {}
        self.run_to_ts_map = {}

        # TODO these are controlled by CLI flags, which we should probably handle as a group.
        self.write_mrc: bool = True
        self.write_zarr: bool = True

        with open(config_path, "r") as conffile:
            confdata = conffile.read()
            config = yaml.safe_load(confdata)

            self.object_configs = {}
            for item in object_classes:
                if config.get(item.plural_key):
                    self.object_configs[item.type_key] = config.pop(item.plural_key)

            # Copy the remaining standardization config keys over to this object.
            for k, v in config.get("standardization_config", {}).items():
                if "regex" in k:
                    v = re.compile(v)
                setattr(self, k, v)

        self.overrides = config.get("overrides")
        self.input_path = f"{input_bucket}/{self.source_prefix}"
        self.dataset_root_dir = f"{input_bucket}/{self.source_prefix}"
        self.deposition_root_dir = f"{input_bucket}/{self.source_prefix}"

    def load_run_data_map(self) -> None:
        self.run_data_map = self.load_run_metadata_file("run_data_map_file")

    def load_map_files(self) -> None:
        self.load_run_tomo_map()
        self.load_run_frame_map()
        self.load_run_ts_map()
        self.load_run_data_map()

    def load_run_metadata_file(self, file_attr: str) -> dict[str, Any]:
        mapdata = {}
        map_filename = None
        with contextlib.suppress(AttributeError):
            map_filename = getattr(self, file_attr)
        if not map_filename:
            return mapdata
        with self.fs.open(os.path.join(self.input_path, map_filename), "r") as tsvfile:
            if map_filename.endswith("tsv"):
                reader = csv.DictReader(tsvfile, delimiter="\t")
            else:
                reader = csv.DictReader(tsvfile)
            for row in reader:
                mapdata[row["run_name"]] = row
        return mapdata

    def get_object_configs(self, key: str) -> Any:
        items = self.object_configs.get(key, [])
        return items

    # This is for tests only. Please don't use it!
    def _set_object_configs(self, key: str, config: list[dict[str, Any]]) -> None:
        self.object_configs[key] = config

    def load_run_csv_file(self, file_attr: str) -> dict[str, Any]:
        mapdata = {}
        map_filename = None
        with contextlib.suppress(AttributeError):
            map_filename = getattr(self, file_attr)
        if not map_filename:
            return mapdata
        with self.fs.open(os.path.join(self.input_path, map_filename), "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                mapdata[row[0]] = row[1]
        return mapdata

    def load_run_tomo_map(self) -> None:
        self.run_to_tomo_map = self.load_run_csv_file("run_to_tomo_map_csv")

    def load_run_frame_map(self) -> None:
        self.run_to_frame_map = self.load_run_csv_file("run_to_frame_map_csv")

    def load_run_ts_map(self) -> None:
        self.run_to_ts_map = self.load_run_csv_file("run_to_ts_map_csv")

    @classmethod
    def get_dataset_name(cls, obj: BaseImporter) -> str:
        try:
            ds = obj.get_dataset()
            if ds:
                return ds.name
        except ValueError:
            pass
        return ""

    @classmethod
    def get_run_name(cls, obj: BaseImporter) -> str:
        try:
            run = obj.get_run()
            if run:
                return run.name
        except ValueError:
            pass
        return ""

    def get_output_path(self, obj: BaseImporter) -> str:
        key = f"{obj.type_key}"
        return self.resolve_output_path(key, obj)

    def get_run_data_map(self, run_name: str) -> dict[str, Any]:
        if map_vars := self.run_data_map.get(run_name):
            return deepcopy(map_vars)
        return {}

    def expand_string(self, run_name: str, string_template: Any) -> int | float | str:
        if not isinstance(string_template, str):
            return string_template
        if run_data := self.get_run_data_map(run_name):
            string_template = string_template.format(**run_data)

            # typing hacks :'(
            if string_template.startswith("int "):
                return int(string_template[4:])
            elif string_template.startswith("float "):
                return float(string_template[6:])
        return string_template

    def expand_metadata(self, run_name: str, metadata_dict: dict[str, Any]) -> dict[str, Any]:
        for k, v in metadata_dict.items():
            if isinstance(v, str):
                metadata_dict[k] = self.expand_string(run_name, v)
            elif isinstance(v, dict):
                metadata_dict[k] = self.expand_metadata(run_name, v)
            elif isinstance(v, list):
                for idx in range(len(v)):
                    # Note - we're not supporting deeply nested lists,
                    # but we don't need to with our current data model.
                    item = v[idx]
                    if isinstance(item, str):
                        v[idx] = self.expand_string(run_name, item)
        return metadata_dict

    def get_expanded_metadata(self, obj: BaseImporter) -> dict[str, Any]:
        metadata_type = obj.type_key
        base_metadata = deepcopy(obj.metadata)
        if metadata_type not in ["tomogram", "tiltseries", "frame"]:
            return base_metadata

        run_name = self.get_run_name(obj)
        base_metadata = self.expand_metadata(run_name, base_metadata)
        return base_metadata

    def get_metadata_path(self, obj: BaseImporter) -> str:
        key = f"{obj.type_key}_metadata"
        return self.resolve_output_path(key, obj)

    def resolve_output_path(self, key: str, obj: BaseImporter, extra_glob_vars: dict = None) -> str:
        from importers.utils import get_importer_output_path

        output_prefix = self.output_prefix
        glob_vars = obj.get_glob_vars()
        if extra_glob_vars:
            glob_vars.update(extra_glob_vars)
        path = os.path.join(output_prefix, get_importer_output_path(key).format(**glob_vars))

        # If the path contains a wildcard, we don't want to create the directory
        if "*" in path or "?" in path:
            return path

        if ".json" in path or ".mrc" in path or ".zarr" in path:
            self.fs.makedirs(os.path.dirname(path))
        else:
            self.fs.makedirs(path)
        return path

    def glob_files(self, obj: BaseImporter, globstring: str) -> list[str]:
        run = obj.get_run()
        if not globstring:
            return []
        globvars = obj.get_glob_vars()
        with contextlib.suppress(ValueError):
            globvars["int_run_name"] = int(run.name)
        expanded_glob = os.path.join(self.dataset_root_dir, globstring.format(**globvars))
        results = self.fs.glob(expanded_glob)
        if not results:
            results = []
        return results

    def to_formatted_path(self, path: str) -> str:
        """
        Returns the s3 key, without the bucket name, for the given path. Helpful for formatting paths in metadata.
        """
        if path:
            if path.startswith(self.output_prefix):
                return os.path.relpath(path, self.output_prefix)
            return path
        return None
