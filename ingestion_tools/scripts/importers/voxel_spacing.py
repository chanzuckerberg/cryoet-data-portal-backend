import contextlib
import json
import os
import re
from typing import TYPE_CHECKING, Any

from common.config import DepositionImportConfig
from common.finders import (
    BaseFinder,
    BaseLiteralValueFinder,
    DepositionObjectImporterFactory,
    DestinationGlobFinder,
    SourceGlobFinder,
)
from common.fs import FileSystemApi
from common.image import get_voxel_size
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.run import RunImporter
else:
    RunImporter = "RunImporter"


class VoxelSpacingLiteralValueFinder(BaseLiteralValueFinder):
    def find(self, config: DepositionImportConfig, fs: FileSystemApi, glob_vars: dict[str, Any]):
        values = {}
        for item in self.literal_value:
            # Do we have a template to expand?
            if isinstance(item, str) and "{" in item:
                values[round(float(config.expand_string(glob_vars["run_name"], item)), 3)] = None
                continue
            values[item] = None
        return values


class TomogramHeaderFinder(BaseFinder):
    def __init__(self, list_glob: str, match_regex: str, header_key: str):
        self.list_glob = list_glob
        self.header_key = header_key
        if not match_regex:
            self.match_regex = re.compile(".*")
        else:
            self.match_regex = re.compile(match_regex)

    def find(self, config: DepositionImportConfig, fs: FileSystemApi, glob_vars: dict[str, Any]):
        # Expand voxel spacing based on tomogram metadata. This is for reverse compatibility with certain configs with run overrides.
        path = os.path.join(config.deposition_root_dir, self.list_glob.format(**glob_vars))
        responses = {}
        for fname in config.fs.glob(path):
            if not self.match_regex.search(fname):
                continue
            path = fname
            # Make this extensible to support other tomo metadata later if need be.
            if self.header_key == "voxel_size":
                size = get_voxel_size(fs, path).item()
                responses[size] = ""
            else:
                raise Exception("invalid header key")
        return responses


class VSImporterFactory(DepositionObjectImporterFactory):
    def load(
        self,
        config: DepositionImportConfig,
        fs: FileSystemApi,
        **parent_objects: dict[str, Any] | None,
    ) -> BaseFinder:
        source = self.source
        if source.get("source_glob"):
            return SourceGlobFinder(**source["source_glob"])
        if source.get("destination_glob"):
            return DestinationGlobFinder(**source["destination_glob"])
        if source.get("tomogram_header"):
            return TomogramHeaderFinder(**source["tomogram_header"])
        if source.get("literal"):
            return VoxelSpacingLiteralValueFinder(**source["literal"])
        raise Exception("Invalid source type")


class VoxelSpacingImporter(BaseImporter):
    type_key = "voxel_spacing"
    finder_factory = VSImporterFactory
    dependencies = ["run"]
    has_metadata = False

    def __init__(
        self,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ):
        super().__init__(*args, **kwargs)
        self.set_voxel_spacing(self.name)

    # TODO mutating importers is bad news :'(
    def set_voxel_spacing(self, voxel_spacing):
        self.name = self.format_voxel_spacing(float(voxel_spacing))

    @classmethod
    def format_voxel_spacing(cls, voxel_spacing: float) -> None:
        return "{:.3f}".format(round(voxel_spacing, 3))

    def get_voxel_spacing(self):
        return self.name

    def get_existing_annotation_metadatas(self, fs):
        # TODO use an annotation finder object here when we have one.
        metadata_glob = f"{self.config.resolve_output_path('annotation', self)}/*.json"
        metadatas = {}
        for file in fs.glob(metadata_glob):
            identifier = os.path.basename(file).split("-")[0]
            with contextlib.suppress(ValueError, TypeError):
                metadatas[int(identifier)] = json.loads(fs.open(file, "r").read())
        return metadatas
