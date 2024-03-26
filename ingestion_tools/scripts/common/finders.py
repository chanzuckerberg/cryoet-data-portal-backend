import re
from dataclasses import dataclass
from common.fs import FileSystemApi
from typing import TYPE_CHECKING, Any
from abc import ABC, abstractclassmethod, abstractmethod
import os

if TYPE_CHECKING:
    from common.config import DepositionImportConfig
else:
    DepositionImportConfig = "DepositionImportConfig"
    DatasetImporter = "DatasetImporter"

### 
### Base Finders
### 
class SourceGlobFinder(ABC):
    list_glob: str
    match_regex: re.Pattern[str]
    name_regex: re.Pattern[str]

    def __init__(self, list_glob: str, match_regex: re.Pattern[str], name_regex: re.Pattern[str]):
        self.list_glob = list_glob
        self.match_regex = re.compile(match_regex)
        self.name_regex = re.compile(name_regex)
    
    def find(self, config: DepositionImportConfig, fs: FileSystemApi, glob_vars: dict[str, Any]):
        expanded_glob = os.path.join(config.dataset_root_dir, self.list_glob.format(**glob_vars))
        path = os.path.join(config.input_path, expanded_glob)
        print(f"path -- {path}")
        responses = {}
        for fname in config.fs.glob(path):
            if not self.match_regex.search(fname):
                continue
            path = fname
            obj_name = self.name_regex.match(os.path.basename(path))[1]
            responses[path] = obj_name
        return responses

# TODO this thing probably shouldn't exist, since it relies on a particular existing state of our
# output directories, but for the moment we have a deposition that doesn't encode voxel spacings in it,
# so this is about the best we can do.
class DestinationGlobFinder(ABC):
    list_glob: str
    match_regex: re.Pattern[str]
    name_regex: re.Pattern[str]

    def __init__(self, list_glob: str, match_regex: re.Pattern[str], name_regex: re.Pattern[str]):
        self.list_glob = list_glob
        self.match_regex = re.compile(match_regex)
        self.name_regex = re.compile(name_regex)
    
    def find(self, config: DepositionImportConfig, fs: FileSystemApi, glob_vars: dict[str, Any]):
        expanded_glob = os.path.join(config.dataset_root_dir, self.list_glob.format(**glob_vars))
        path = os.path.join(config.input_path, expanded_glob)
        print(f"path -- {path}")
        responses = {}
        for fname in config.fs.glob(path):
            if not self.match_regex.search(fname):
                continue
            path = fname
            obj_name = self.name_regex.match(os.path.basename(path))[1]
            responses[path] = obj_name
        return responses

class BaseLiteralValueFinder(ABC):
    literal_value: list[Any]

    def __init__(self, literal_value: str):
        self.literal_value = literal_value

    def find(self, config: DepositionImportConfig, fs: FileSystemApi):
        return self.literal_value

### 
### Dataset finders
### 
class DatasetDestinationGlobFinder(DestinationGlobFinder):
    pass

class DatasetSourceGlobFinder(SourceGlobFinder):
    pass

class DatasetLiteralFinder(BaseLiteralValueFinder):
    pass

class RunDestinationGlobFinder(DestinationGlobFinder):
    pass

class RunSourceGlobFinder(SourceGlobFinder):
    pass

class RunLiteralFinder(BaseLiteralValueFinder):
    pass

class VSDestinationGlobFinder(DestinationGlobFinder):
    pass

class VSSourceGlobFinder(SourceGlobFinder):
    pass

class VSLiteralFinder(BaseLiteralValueFinder):
    pass

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
        for path, name in found.items():
            results.append(cls(config=config, parent=parent_object, name=name, path=path))
        for item in results:
            print(f":::: {item.name} -- {item.path}")
        return results

class DatasetImporterFactory(DepositionObjectImporterFactory):
    def load(self, parent_object: Any | None, config: DepositionImportConfig, fs: FileSystemApi):
        source = self.source
        if source.get('source_glob'):
            return DatasetSourceGlobFinder(**source['source_glob'])
        if source.get('destination_glob'):
            return DatasetDestinationGlobFinder(**source['destination_glob'])
        if source.get('literal'):
            return DatasetLiteralFinder(**source['tomogram_header'])
        raise Exception("Invalid source type")

class RunImporterFactory(DepositionObjectImporterFactory):
    def load(self, parent_object: Any | None, config: DepositionImportConfig, fs: FileSystemApi):
        source = self.source
        if source.get('source_glob'):
            return RunSourceGlobFinder(**source['source_glob'])
        if source.get('destination_glob'):
            return RunDestinationGlobFinder(**source['destination_glob'])
        if source.get('literal'):
            return RunLiteralFinder(**source['tomogram_header'])
        raise Exception("Invalid source type")

class VSImporterFactory(DepositionObjectImporterFactory):
    def load(self, parent_object: Any | None, config: DepositionImportConfig, fs: FileSystemApi):
        source = self.source
        if source.get('source_glob'):
            return VSSourceGlobFinder(**source['source_glob'])
        if source.get('destination_glob'):
            return VSDestinationGlobFinder(**source['destination_glob'])
        if source.get('literal'):
            return VSLiteralFinder(**source['tomogram_header'])
        raise Exception("Invalid source type")