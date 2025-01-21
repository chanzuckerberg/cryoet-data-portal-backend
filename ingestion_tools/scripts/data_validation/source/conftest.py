import os
import pathlib

import pytest
from importers.utils import IMPORTERS

from common.fs import FileSystemApi, S3Filesystem
from data_validation.source.fixtures.parameterized import CryoetTestEntities


def pytest_addoption(parser: pytest.Parser) -> None:
    """Common options for all tests."""

    # S3 or local
    parser.addoption("--input-bucket", action="store", required=True)

    # optional output path. Only needed if the config has destination globs.
    parser.addoption("--output-bucket", action="store", default="cryoet-data-portal-staging")

    # File path to the ingestion config file relative to the dataset_config
    parser.addoption("--ingestion-config", action="store", type=pathlib.Path, required=True)

    for importer in IMPORTERS:
        parser.addoption(f"--filter-{importer.type_key}-name", action="store", default=None)


def ingestion_config_path(config: pytest.Config) -> str:
    config_path = config.getoption("--ingestion-config")
    return os.path.abspath(os.path.join(os.getcwd(), "..", "..", "..", "dataset_configs", config_path))

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    # Using pytest_generate_tests to parametrize the fixtures causes the per-run-fixtures to be run multiple times,
    # but setting the parameterization as labels and parametrizing the class with that label leads to desired outcome, i.e.
    # re-use of the per-run fixtures.
    pytest.cryoet = CryoetTestEntities(config, ingestion_config_path(config))

@pytest.fixture(scope="session")
def filesystem() -> S3Filesystem:
    return FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)
