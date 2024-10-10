
import logging
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from db_import.common.config import DBImportConfig

from platformics.database.models.base import Base

logger = logging.getLogger("db_import")

if TYPE_CHECKING:
    from db_import.importers.base import ItemDBImporter
else:
    ItemDBImporter = Any


class ItemFinder(ABC):
    @abstractmethod
    def __init__(self, config: DBImportConfig, **kwargs):
        pass

    @abstractmethod
    def find(self, item_importer: ItemDBImporter) -> list[ItemDBImporter]:
        pass


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
        for file in self.config.glob_s3(self.path, self.glob, is_file=True):
            if self.match_regex.match(file):
                data = {"file": file}
                data.update(parents)
                results.append(item_importer(self.config, data))
        return results
