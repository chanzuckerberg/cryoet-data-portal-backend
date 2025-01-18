import os
import re
from typing import List

import pytest
from importers.base_importer import BaseImporter
from importers.dataset import DatasetImporter
from importers.deposition import DepositionImporter
from importers.run import RunImporter
from importers.utils import IMPORTERS

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


def get_entities(ingestion_config: DepositionImportConfig, importer_class: BaseImporter, parents: List[BaseImporter], request: pytest.FixtureRequest) -> List[BaseImporter]:
    items = []
    name_filter = request.config.getoption(f"--{importer_class.type_key}-name-filter")
    name_regex = re.compile(name_filter) if name_filter else None
    for parent in parents:
        new_items = [
            instance
            for instance in importer_class.finder(ingestion_config, **{parent.type_key: parent})
            if not name_regex or name_regex.match(instance.name)
        ]
        items.extend(new_items)
    print(f"Found {len(items)} {importer_class.type_key} entities")
    print([item.name for item in items])
    return items


@pytest.fixture(scope="session")
def input_bucket(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--input-bucket")


@pytest.fixture(scope="session")
def output_bucket(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--output-bucket")


@pytest.fixture(scope="session")
def ingestion_config_path(request: pytest.FixtureRequest) -> str:
    config_path = request.config.getoption("--ingestion-config")
    return os.path.abspath(os.path.join(os.getcwd(), "..", "..", "..", "dataset_configs", config_path))


@pytest.fixture(scope="session")
def ingestion_config(output_bucket: str, input_bucket: str, ingestion_config_path: str) -> DepositionImportConfig:
    fs = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)
    return DepositionImportConfig(fs, ingestion_config_path, output_bucket, input_bucket, IMPORTERS)

@pytest.fixture(scope="session")
def deposition(ingestion_config: DepositionImportConfig, request: pytest.FixtureRequest) -> DepositionImporter:
    depositions = list(DepositionImporter.finder(ingestion_config))
    return depositions[0]

@pytest.fixture(scope="session")
def datasets(ingestion_config: DepositionImportConfig, deposition: DepositionImporter, request: pytest.FixtureRequest) -> List[DatasetImporter]:
    return get_entities(ingestion_config, DatasetImporter, [deposition], request)

@pytest.fixture(scope="session")
def runs(ingestion_config: DepositionImportConfig, datasets: List[DatasetImporter], request: pytest.FixtureRequest) -> List[RunImporter]:
    return get_entities(ingestion_config, RunImporter, datasets, request)
