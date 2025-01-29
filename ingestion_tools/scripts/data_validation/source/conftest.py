import os
import pathlib

import allure
import pytest
from importers.base_importer import BaseImporter
from importers.utils import IMPORTERS

from data_validation.source.fixtures.data import *  # noqa: E402, F403
from data_validation.source.fixtures.parameterized import CryoetSourceEntities


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
    pytest.cryoet = CryoetSourceEntities(config, ingestion_config_path(config))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item):
    """
    This hook integrates allure to dynamically annotate the test reports with
    details such as the dataset, run, and voxel spacing being tested.
    """
    if "run" in item.fixturenames:
        run = item.callspec.params['run']
        allure.dynamic.feature(f"Run {run.name}")
        allure.dynamic.epic(f"Dataset {run.get_dataset().name}")
    elif "tiltseries" in item.fixturenames:
        run_children = [val for val in item.callspec.params.values() if isinstance(val, BaseImporter)]
        if run_children:
            run = run_children[0].get_run()
            allure.dynamic.feature(f"Run {run.name}")
            allure.dynamic.epic(f"Dataset {run.get_dataset().name}")

    if "voxel_spacing" in item.fixturenames:
        allure.dynamic.story(f"VoxelSpacing {item.callspec.params['voxel_spacing'].name}")

    yield
