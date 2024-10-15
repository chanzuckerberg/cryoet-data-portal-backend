import json
import logging
import os
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from db_import.common.config import DBImportConfig

from platformics.database.models.base import Base

logger = logging.getLogger("finders")

if TYPE_CHECKING:
    from db_import.importers.base import ItemDBImporter
else:
    ItemDBImporter = Any


class ItemFinder(ABC):
    def __init__(self, config: DBImportConfig, **kwargs):
        self.config = config

    @abstractmethod
    def find(self, item_importer: ItemDBImporter) -> list[ItemDBImporter]:
        pass

    def strip_bucket_from_path(self, path):
        if path.startswith(self.config.bucket_name):
            return path[len(self.config.bucket_name) + 1 :]
        return path

    def recursive_glob(self, prefix: str, target_glob: str) -> list[str]:
        s3 = self.config.s3fs
        prefix = prefix.rstrip("/")
        logger.info("Recursively looking for files in %s/%s", prefix, target_glob)
        return s3.glob(os.path.join(prefix, target_glob))

    def glob_s3(self, prefix: str, glob_string: str, is_file: bool = True):
        s3 = self.config.s3fs
        prefix = prefix.rstrip("/")
        if glob_string:
            prefix = os.path.join(prefix, glob_string)
        logger.info("Looking for files in %s", prefix)
        for item in s3.glob(prefix):
            if is_file and not s3.isfile(item):
                continue
            yield item

    def load_metadata(self, key: str, is_file_required: bool = True) -> dict[str, Any] | None:
        """
        Loads file matching the key value as json. If file does not exist, will raise error if is_file_required is True
        else it will return None.
        """
        s3 = self.config.s3fs
        data = json.loads(s3.cat_file(key))
        return data


class FileFinder(ItemFinder):
    def __init__(self, config: DBImportConfig, path: str, glob: str, match_regex: str | None):
        self.config = config
        self.path = path
        self.glob = glob
        self.match_regex = None
        if match_regex:
            self.match_regex = re.compile(match_regex)

    def find(self, item_importer: ItemDBImporter, parents: dict[str, Base]) -> list[ItemDBImporter]:
        results: list[ItemDBImporter] = []
        for file in self.glob_s3(self.path, self.glob, is_file=True):
            if self.match_regex.match(file):
                data = {"file": self.strip_bucket_from_path(file)}
                data.update(parents)
                results.append(item_importer(self.config, data))
        return results


class MetadataFileFinder(ItemFinder):
    def __init__(self, config: DBImportConfig, path: str, file_glob: str, list_key: str | None = None):
        self.config = config
        self.path = path
        self.file_glob = file_glob
        self.list_key = list_key

    def find(self, item_importer: ItemDBImporter, parents: dict[str, Base]) -> list[ItemDBImporter]:
        results: list[ItemDBImporter] = []
        for file in self.recursive_glob(self.path, self.file_glob):
            json_data = self.load_metadata(file)
            if self.list_key:
                for idx, item in enumerate(json_data[self.list_key]):
                    data = item
                    data["file"] = self.strip_bucket_from_path(file)
                    data["index"] = idx + 1  # Use a 1-based index for humans.
                    data.update(parents)
                    results.append(item_importer(self.config, data))
                # If we have a list key, we don't want to continue
                continue
            data = {"file": self.strip_bucket_from_path(file)}
            data.update(parents)
            data.update(json_data)
            results.append(item_importer(self.config, data))
        return results
