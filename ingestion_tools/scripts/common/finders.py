import os
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from common.fs import FileSystemApi
from common.image import get_voxel_size

if TYPE_CHECKING:
    from common.config import DepositionImportConfig
else:
    DepositionImportConfig = "DepositionImportConfig"
    DatasetImporter = "DatasetImporter"


###
### Base Finders
###
class SourceMultiGlobFinder:
    list_glob: str
    match_regex: re.Pattern[str]
    name_regex: re.Pattern[str]

    def __init__(self, list_globs: str):
        self.list_globs = list_globs

    def find(self, config: DepositionImportConfig, fs: FileSystemApi, glob_vars: dict[str, Any]):
        responses = {}
        for list_glob in self.list_globs:
            path = os.path.join(config.deposition_root_dir, list_glob.format(**glob_vars))
            for fname in config.fs.glob(path):
                if not self.match_regex.search(fname):
                    continue
                path = fname
                obj_name = self.name_regex.match(os.path.basename(path))[1]
                responses[obj_name] = path
        return responses


class SourceGlobFinder:
    list_glob: str
    match_regex: re.Pattern[str]
    name_regex: re.Pattern[str]

    def __init__(
        self,
        list_glob: str,
        match_regex: re.Pattern[str] | None = None,
        name_regex: re.Pattern[str] | None = None,
    ):
        self.list_glob = list_glob
        if not match_regex:
            self.match_regex = re.compile(".*")
        else:
            self.match_regex = re.compile(match_regex)
        if not name_regex:
            self.name_regex = re.compile("(.*)")
        else:
            self.name_regex = re.compile(name_regex)

    def find(self, config: DepositionImportConfig, fs: FileSystemApi, glob_vars: dict[str, Any]):
        path = os.path.join(config.deposition_root_dir, self.list_glob.format(**glob_vars))
        responses = {}
        for fname in config.fs.glob(path):
            if not self.match_regex.search(fname):
                continue
            path = fname
            obj_name = self.name_regex.match(os.path.basename(path))[1]
            responses[obj_name] = path
        return responses


# TODO this thing probably shouldn't exist, since it relies on a particular existing state of our
# output directories, but for the moment we have a deposition that doesn't encode voxel spacings in it,
# so this is about the best we can do.
class DestinationGlobFinder:
    list_glob: str
    match_regex: re.Pattern[str]
    name_regex: re.Pattern[str]

    def __init__(self, list_glob: str, match_regex: re.Pattern[str], name_regex: re.Pattern[str]):
        self.list_glob = list_glob
        self.match_regex = re.compile(match_regex)
        self.name_regex = re.compile(name_regex)

    def find(self, config: DepositionImportConfig, fs: FileSystemApi, glob_vars: dict[str, Any]):
        path = os.path.join(self.list_glob.format(**glob_vars))
        responses = {}
        for fname in config.fs.glob(path):
            if not self.match_regex.search(fname):
                continue
            path = fname
            obj_name = self.name_regex.match(os.path.basename(path))[1]
            responses[obj_name] = path
        return responses


class BaseLiteralValueFinder:
    literal_value: list[Any]

    def __init__(self, value: str):
        self.literal_value = value

    def find(self, config: DepositionImportConfig, fs: FileSystemApi, glob_vars: dict[str, Any]):
        return {item: None for item in self.literal_value}


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


class TomogramHeaderFinder:
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


###
### Factories
###
class DepositionObjectImporterFactory(ABC):
    def __init__(self, source: dict[str, Any]):
        self.source = source

    @abstractmethod
    def load(self, expansion_data: dict, config: DepositionImportConfig, fs: FileSystemApi):
        pass

    # TODO FIXME -- passing in the class-to-instantiate is a temporary hack to work around
    # python circular import shenanigans. We should try to refactor this out and have each
    # factory create the specific object types it's supposed to create, so we can customize
    # instantiation per object type when we need it.
    def find(self, cls, parent_object: Any | None, config: DepositionImportConfig, fs: FileSystemApi):
        loader = self.load(parent_object, config, fs)
        glob_vars = {}
        if parent_object:
            glob_vars = parent_object.get_glob_vars()
        tmp_parent_object = parent_object
        while tmp_parent_object:
            glob_vars[f"{tmp_parent_object.type_key}_output_path"] = tmp_parent_object.get_output_path()
            tmp_parent_object = tmp_parent_object.parent
        found = loader.find(config, fs, glob_vars)
        results = []
        for name, path in found.items():
            results.append(cls(config=config, parent=parent_object, name=name, path=path))
        return results


class DefaultImporterFactory(DepositionObjectImporterFactory):
    def load(self, parent_object: Any | None, config: DepositionImportConfig, fs: FileSystemApi):
        source = self.source
        if source.get("source_glob"):
            return SourceGlobFinder(**source["source_glob"])
        if source.get("source_multi_glob"):
            return SourceMultiGlobFinder(**source["source_multi_glob"])
        if source.get("destination_glob"):
            return DestinationGlobFinder(**source["destination_glob"])
        if source.get("literal"):
            return BaseLiteralValueFinder(**source["literal"])
        raise Exception("Invalid source type")


# TODO - This one's gonna need to get fancy to inspect tomogram headers.
class VSImporterFactory(DepositionObjectImporterFactory):
    def load(self, parent_object: Any | None, config: DepositionImportConfig, fs: FileSystemApi):
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


class RawTiltImporterFactory(DefaultImporterFactory):
    pass


class TiltseriesImporterFactory(DefaultImporterFactory):
    pass


class FrameImporterFactory(DefaultImporterFactory):
    pass


class GainImporterFactory(DefaultImporterFactory):
    pass


class TomogramImporterFactory(DefaultImporterFactory):
    pass


class DatasetImporterFactory(DefaultImporterFactory):
    pass


class RunImporterFactory(DefaultImporterFactory):
    pass


class KeyImageImporterFactory(DefaultImporterFactory):
    pass


# TODO, how is this going to work???
class AnnotationImporterFactory(DefaultImporterFactory):
    pass
