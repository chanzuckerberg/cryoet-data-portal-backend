import pathlib

import pytest
from importers.utils import IMPORTERS


def pytest_addoption(parser: pytest.Parser) -> None:
    """Common options for all tests."""

    # S3 or local
    parser.addoption("--input-bucket", action="store", required=True)

    # optional output path. Only needed if the config has destination globs.
    parser.addoption("--output-bucket", action="store", default="cryoet-data-portal-staging")

    # File path to the ingestion config file relative to the dataset_config
    parser.addoption("--ingestion-config", action="store", type=pathlib.Path, required=True)

    for importer in IMPORTERS:
        parser.addoption(f"--{importer.type_key}-name-filter", action="store", default=None)
