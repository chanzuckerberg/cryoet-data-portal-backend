import json
import os
from collections import defaultdict
from functools import partial
from typing import Any

from common.config import DepositionImportConfig


# This class is a global var that caches metadata and identifiers for entities,
# so we can generate non-conflicting sequential identifiers for entities as they're imported.
class IdentifierHelper:
    next_identifier: dict[str, int] = defaultdict(partial(int, 100))
    cached_identifiers: dict[str, int] = {}
    loaded_containers: set[str] = set()

    @classmethod
    def get_identifier(
        cls,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        parents: dict[str, Any],
        *args,
        **kwargs,
    ):
        container_key = cls._get_container_key(config, parents, *args, **kwargs)
        cls._load_ids_for_container(container_key, config, parents, *args, **kwargs)

        current_ids_key = cls._generate_hash_key(container_key, metadata, parents, *args, **kwargs)
        if cached_id := cls.cached_identifiers.get(current_ids_key):
            return cached_id

        return_value = cls.next_identifier[container_key]
        cls.cached_identifiers[current_ids_key] = return_value
        cls.next_identifier[container_key] += 1
        return return_value

    @classmethod
    def _load_ids_for_container(
        cls,
        container_key: str,
        config: DepositionImportConfig,
        parents: dict[str, Any],
        *args,
        **kwargs,
    ):
        if container_key in cls.loaded_containers:
            return
        metadata_glob = cls._get_metadata_glob(config, parents, *args, **kwargs)
        for file in config.fs.glob(metadata_glob):
            identifier = int(os.path.basename(file).split("-")[0])
            if identifier >= cls.next_identifier[container_key]:
                cls.next_identifier[container_key] = identifier + 1
            metadata = json.loads(config.fs.open(file, "r").read())
            current_ids_key = cls._generate_hash_key(container_key, metadata, parents, *args, **kwargs)
            cls.cached_identifiers[current_ids_key] = identifier
        cls.loaded_containers.add(container_key)

    @classmethod
    def _generate_hash_key(
        cls,
        container_key: str,
        metadata: dict[str, Any],
        parents: dict[str, Any],
        *args,
        **kwargs,
    ) -> str:
        # Select specific values from metadata for hash generation
        # This needs to be adjusted based on the structure of each metadata
        raise NotImplementedError("_generate_hash_key must be implemented in subclass")

    @classmethod
    def _get_metadata_glob(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        # Glob for fetching relevant metadata files
        raise NotImplementedError("_get_metadata_glob must be implemented in subclass")

    @classmethod
    def _get_container_key(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs):
        # This is value will be used to ensure we don't _load_current_ids for a folder multiple times
        raise NotImplementedError("_get_container_key must be implemented in subclass")
