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


class DataImportConfig:
    https_prefix = os.getenv("DOMAIN_NAME", "https://files.cryoetdataportal.cziscience.com")
    source_prefix: str
    destination_prefix: str
    fs: FileSystemApi
    run_glob: str
    run_regex: re.Pattern[str]
    tomo_glob: str
    tomo_format: str
    tomo_regex: re.Pattern[str] | None = None
    tomo_key_photo_glob: str | None = None
    tomo_voxel_size: str
    ts_name_regex: re.Pattern[str] | None = None
    run_name_regex: re.Pattern[str]
    frames_name_regex: re.Pattern[str] | None = None
    frames_glob: str
    tiltseries_glob: str | None = None
    run_to_tomo_map_file: str | None = None
    run_to_tomo_map: dict[str, str] | None = None
    run_to_frame_map_csv: str | None = None
    run_to_frame_map: dict[str, str] | None = None
    run_to_ts_map_csv: str | None = None
    run_to_ts_map: dict[str, str] | None = None
    gain_glob: str
    rawtlt_files: list[str] | None = None
    # metadata templates
    dataset_template: dict[str, Any]
    run_template: dict[str, Any]
    tomogram_template: dict[str, Any]
    tiltseries_template: dict[str, Any]
    annotation_template: dict[str, Any]
    output_prefix: str
    input_prefix: str
    overrides_by_run: list[RunOverride] | None = None
    run_data_map: dict[str, Any]
    run_data_map_file: str | None = None

    def __init__(self, fs: FileSystemApi, config_path: str, output_prefix: str, input_bucket: str):
        self.output_prefix = output_prefix
        self.fs = fs
        with open(config_path, "r") as conffile:
            dataset_config = yaml.safe_load(conffile)
            config = dataset_config["standardization_config"]

            for k, v in config.items():
                if "regex" in k:
                    v = re.compile(v)
                setattr(self, k, v)

            self.overrides_by_run = []
            try:
                for item in dataset_config["overrides_by_run"]:
                    override = RunOverride(
                        run_regex=re.compile(item["run_regex"]),
                        tomograms=item.get("tomograms"),
                        tiltseries=item.get("tiltseries"),
                    )
                    self.overrides_by_run.append(override)
            except KeyError:
                # This isn't a required field
                pass

        template_configs = {
            "runs": "run",
            "tomograms": "tomogram",
            "tiltseries": "tiltseries",
            "dataset": "dataset",
            "annotations": "annotation",
        }
        for config_key, template_key in template_configs.items():
            setattr(self, f"{template_key}_template", dataset_config[config_key])
        self.input_path = f"{input_bucket}/{self.source_prefix}"
        self.dataset_root_dir = f"{input_bucket}/{self.source_prefix}"

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
        with self.fs.open(f"{self.input_path}/{map_filename}", "r") as tsvfile:
            if map_filename.endswith("tsv"):
                reader = csv.DictReader(tsvfile, delimiter="\t")
            else:
                reader = csv.DictReader(tsvfile)
            for row in reader:
                mapdata[row["run_name"]] = row
        return mapdata

    def load_run_csv_file(self, file_attr: str) -> dict[str, Any]:
        mapdata = {}
        map_filename = None
        with contextlib.suppress(AttributeError):
            map_filename = getattr(self, file_attr)
        if not map_filename:
            return mapdata
        with self.fs.open(f"{self.input_path}/{map_filename}", "r") as csvfile:
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
    def get_run_name(cls, obj: BaseImporter) -> str:
        try:
            run = obj.get_run()
            if run:
                return run.run_name
        except ValueError:
            pass
        return ""

    @classmethod
    def get_run_voxelsize(cls, obj: BaseImporter) -> float:
        try:
            run = obj.get_run()
            if run:
                return run.voxel_spacing
        except ValueError:
            pass
        return 0

    def get_output_path(self, obj: BaseImporter) -> str:
        key = f"{obj.type_key}"
        return self.resolve_output_path(key, self.get_run_name(obj), self.get_run_voxelsize(obj))

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
        # hacky pluralization, look away!!
        plural_map = {
            "tomogram": "tomograms",
            "tiltseries": "tiltseries",
        }
        base_metadata = deepcopy(getattr(self, f"{metadata_type}_template"))
        if metadata_type not in ["tomogram", "tiltseries"]:
            return base_metadata

        run_name = self.get_run_name(obj)
        base_metadata = self.expand_metadata(run_name, base_metadata)
        if override_data := self.get_run_override(run_name):
            map_key = plural_map[metadata_type]
            if extra_metadata := getattr(override_data, map_key):
                base_metadata.update(extra_metadata)
        return base_metadata

    def get_run_override(self, run_name: str) -> RunOverride | None:
        if not self.overrides_by_run:
            return
        for item in self.overrides_by_run:
            if item.run_regex.match(run_name):
                return item
        return

    def get_metadata_path(self, obj: BaseImporter) -> str:
        key = f"{obj.type_key}_metadata"
        return self.resolve_output_path(key, self.get_run_name(obj), self.get_run_voxelsize(obj))

    def resolve_output_path(self, key: str, run_name: str, voxelsize: float | str) -> str:
        paths = {
            "tomogram": "{run_name}/Tomograms/VoxelSpacing{voxelsize}/CanonicalTomogram",
            "key_image": "{run_name}/Tomograms/VoxelSpacing{voxelsize}/KeyPhotos",
            "tiltseries": "{run_name}/TiltSeries",
            "frames": "{run_name}/Frames",
            "annotation": "{run_name}/Tomograms/VoxelSpacing{voxelsize}/Annotations",
            "annotation_metadata": "{run_name}/Tomograms/VoxelSpacing{voxelsize}/Annotations",
            "run_metadata": "{run_name}/run_metadata.json",
            "tomogram_metadata": "{run_name}/Tomograms/VoxelSpacing{voxelsize}/CanonicalTomogram/tomogram_metadata.json",
            "tiltseries_metadata": "{run_name}/TiltSeries/tiltseries_metadata.json",
            "dataset_metadata": "dataset_metadata.json",
            "dataset_keyphoto": "Images",
            "neuroglancer": "{run_name}/Tomograms/VoxelSpacing{voxelsize}/CanonicalTomogram/neuroglancer_config.json",
        }
        path = os.path.join(
            self.output_prefix,
            self.destination_prefix,
            paths[key].format(run_name=run_name, voxelsize=voxelsize),
        )
        self.fs.makedirs(path)
        return path

    def glob_files(self, obj: BaseImporter, globstring: str) -> list[str]:
        run = obj.get_run()
        if not globstring:
            return []
        globvars = run.get_glob_vars()
        with contextlib.suppress(ValueError):
            globvars["int_run_name"] = int(run.run_name)
        expanded_glob = os.path.join(self.dataset_root_dir, globstring.format(**globvars))
        results = self.fs.glob(expanded_glob)
        if not results:
            results = []
        return results
