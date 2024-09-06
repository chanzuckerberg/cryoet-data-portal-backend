import json
import os
from collections import defaultdict
from functools import partial
from typing import Any

from common.config import DepositionImportConfig


class IdentifierHelper:
    next_identifier: dict[str, int] = defaultdict(partial(int, 100))
    cached_identifiers: dict[str, int] = {}
    loaded_parent_containers: set[str] = {}

    @classmethod
    def _load_current_ids(cls, parent_key: str, config: DepositionImportConfig, *args, **kwargs):
        if parent_key in cls.loaded_parent_containers:
            return
        metadata_glob = cls._get_metadata_glob(config, *args, **kwargs)
        for file in config.fs.glob(metadata_glob):
            identifier = int(os.path.basename(file).split("-")[0])
            if identifier >= cls.next_identifier[parent_key]:
                cls.next_identifier[parent_key] = identifier + 1
            metadata = json.loads(config.fs.open(file, "r").read())
            current_ids_key = cls._get_ids_key(parent_key, metadata, *args, **kwargs)
            cls.cached_identifiers[current_ids_key] = identifier
        cls.loaded_parent_containers.add(parent_key)

    @classmethod
    def _get_ids_key(cls, parent_key: str, metadata: dict[str, Any], parents: dict[str, Any], *args, **kwargs):
        raise NotImplementedError("get_ids_key must be implemented in subclass")

    @classmethod
    def get_identifier(
        cls, config: DepositionImportConfig, metadata: dict[str, Any], parents: dict[str, Any], *args, **kwargs,
    ):
        parent_key = cls._get_parent_key(config, metadata, parents, *args, **kwargs)
        cls._load_current_ids(parent_key, config, *args, **kwargs)

        current_ids_key = cls._get_ids_key(parent_key, metadata, parents, *args, **kwargs)
        if cached_id := cls.cached_identifiers.get(current_ids_key):
            return cached_id

        return_value = cls.next_identifier[parent_key]
        cls.cached_identifiers[current_ids_key] = return_value
        cls.next_identifier[parent_key] += 1
        return return_value

    @classmethod
    def _get_metadata_glob(cls, config: DepositionImportConfig, *args, **kwargs) -> str:
        raise NotImplementedError("get_metadata_glob must be implemented in subclass")

    @classmethod
    def _get_parent_key(
        cls, config: DepositionImportConfig, metadata: dict[str, Any], parents: dict[str, Any], *args, **kwargs,
    ):
        raise NotImplementedError("get_ids_key must be implemented in subclass")
