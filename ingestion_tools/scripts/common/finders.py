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
    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]) -> dict[str, str]:
        pass


class SourceMultiGlobFinder(BaseFinder):
    list_glob: list[str]

    def __init__(self, list_globs: list[str]):
        self.list_globs = list_globs

    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]) -> dict[str, str]:
        responses = {}
        for list_glob in self.list_globs:
            path = os.path.join(config.deposition_root_dir, list_glob.format(**glob_vars))
            for fname in config.fs.glob(path):
                path = fname
                responses[path] = path
        return responses


class SourceGlobFinder(BaseFinder):
    list_glob: str
    match_regex: re.Pattern[str]
    name_regex: re.Pattern[str]

    def __init__(
        self,
        list_glob: str,
        match_regex: str | None = None,
        name_regex: str | None = None,
    ):
        self.list_glob = list_glob
        if not match_regex:
            match_regex = ".*"
        self.match_regex = re.compile(match_regex)

        if not name_regex:
            name_regex = "(.*)"
        self.name_regex = re.compile(name_regex)

    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]) -> dict[str, str]:
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

    def __init__(self, list_glob: str, match_regex: str | None, name_regex: str):
        self.list_glob = list_glob
        if not match_regex:
            match_regex = ".*"
        self.match_regex = re.compile(match_regex)

        if not name_regex:
            name_regex = "(.*)"
        self.name_regex = re.compile(name_regex)

    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]) -> dict[str, str]:
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
    literal_value: list[str] | dict[str, str | None]

    def __init__(self, value: dict[str, str | None] | list[str]):
        self.literal_value = value

    def find(self, config: DepositionImportConfig, glob_vars: dict[str, Any]) -> dict[str, str | None]:
        if isinstance(self.literal_value, dict):
            return self.literal_value
        return {item: None for item in self.literal_value}


###
### Factories
###
class DepositionObjectImporterFactory(ABC):
    def __init__(self, source: dict[str, Any]):
        self.source = source
        parent_filters = source.get("parent_filters", {})
        self.exclude_parents = {}
        self.include_parents = {}
        for parent_key, regex_list in parent_filters.get("include", {}).items():
            self.include_parents[parent_key] = [re.compile(regex_str) for regex_str in regex_list]
        for parent_key, regex_list in parent_filters.get("exclude", {}).items():
            self.exclude_parents[parent_key] = [re.compile(regex_str) for regex_str in regex_list]

    @abstractmethod
    def load(
        self,
        config: DepositionImportConfig,
        **expansion_data: dict[str, Any] | None,
    ) -> BaseFinder:
        pass

    def _should_search(self, **parent_objects: dict[str, Any] | None) -> bool:
        for parent_key, parent_obj in parent_objects.items():
            # Apply include/exclude filters
            if self.exclude_parents.get(parent_key):
                for regex in self.exclude_parents[parent_key]:
                    if regex.search(parent_obj.name):
                        return False
            if self.include_parents.get(parent_key):
                for regex in self.include_parents[parent_key]:
                    # TODO:
                    # how does this work? if you have multiple includes and on any include, if it fails, you exclude?
                    # i was understanding it as you check all the includes, and if all of them don't include, you fail?
                    if not regex.search(parent_obj.name):
                        return False
        return True

    def _get_glob_vars(self, **parent_objects: dict[str, Any] | None):
        glob_vars = {}
        for _, parent_obj in parent_objects.items():
            glob_vars.update(parent_obj.get_glob_vars())
            # These are *only* used by source glob finder, which is kindof a hack :'(
            glob_vars[f"{parent_obj.type_key}_output_path"] = parent_obj.get_output_path()
        return glob_vars

    def _instantiate(
        self,
        cls,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        parents: dict[str, Any] | None,
    ):
        return cls(config=config, metadata=metadata, name=name, path=path, parents=parents)

    def _get_results(
        self,
        cls,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        **parent_objects: dict[str, Any] | None,
    ):
        loader = self.load(config, **parent_objects)
        glob_vars = self._get_glob_vars(**parent_objects)
        found = loader.find(config, glob_vars)
        results = []
        for name, path in found.items():
            item = self._instantiate(cls, config, metadata, name, path, parent_objects)
            if item:
                results.append(item)
        return results

    # This is the main entrypoint into this class that should be called by the importer
    def find(
        self,
        cls,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        **parent_objects: dict[str, Any] | None,
    ):
        if not self._should_search(**parent_objects):
            return []
        return self._get_results(cls, config, metadata, **parent_objects)


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
