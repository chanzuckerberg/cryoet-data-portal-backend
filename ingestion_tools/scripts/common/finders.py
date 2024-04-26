import os
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from common.config import DepositionImportConfig
else:
    DepositionImportConfig = "DepositionImportConfig"


###
### Base Finders
###
class BaseFinder(ABC):
    @abstractmethod
    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]):
        pass


class SourceMultiGlobFinder(BaseFinder):
    list_glob: str
    match_regex: re.Pattern[str]
    name_regex: re.Pattern[str]

    def __init__(self, list_globs: str):
        self.list_globs = list_globs

    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]):
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


class SourceGlobFinder(BaseFinder):
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

    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]):
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
class DestinationGlobFinder(BaseFinder):
    list_glob: str
    match_regex: re.Pattern[str]
    name_regex: re.Pattern[str]

    def __init__(self, list_glob: str, match_regex: re.Pattern[str], name_regex: re.Pattern[str]):
        self.list_glob = list_glob
        self.match_regex = re.compile(match_regex)
        self.name_regex = re.compile(name_regex)

    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]):
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

    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]):
        return {item: None for item in self.literal_value}


###
### Factories
###
class DepositionObjectImporterFactory(ABC):
    def __init__(self, source: dict[str, Any]):
        self.source = source

    @abstractmethod
    def load(
        self,
        config: DepositionImportConfig,
        **expansion_data: dict[str, Any] | None,
    ) -> BaseFinder:
        pass

    def find(
        self,
        cls,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        **parent_objects: dict[str, Any] | None,
    ):
        loader = self.load(config, **parent_objects)
        glob_vars = {}
        for _, parent in parent_objects.items():
            glob_vars.update(parent.get_glob_vars())
        tmp_parent_objects = list(parent_objects.values())
        while True:
            new_parent_objects = []
            for parent in tmp_parent_objects:
                glob_vars[f"{parent.type_key}_output_path"] = parent.get_output_path()
                if parent.parents:
                    new_parent_objects.extend(parent.parents.values())
            if not new_parent_objects:
                break
            tmp_parent_objects = new_parent_objects
        found = loader.find(config, glob_vars)
        results = []
        for name, path in found.items():
            results.append(cls(config=config, metadata=metadata, name=name, path=path, parents=parent_objects))
        return results


class DefaultImporterFactory(DepositionObjectImporterFactory):
    def load(
        self,
        config: DepositionImportConfig,
        **parent_objects: dict[str, Any] | None,
    ) -> BaseFinder:
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
