import pytest
from importers.dataset import DatasetImporter
from importers.run import RunImporter
from importers.voxel_spacing import VoxelSpacingImporter
from standardize_dirs import IMPORTERS

from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from common.fs import FileSystemApi


@pytest.fixture
def dataset_config(s3_fs: FileSystemApi, test_output_bucket: str) -> DepositionImportConfig:
    config_file = "tests/fixtures/annotations/anno_config.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    return config


@pytest.fixture
def parents(dataset_config):
    dataset = DatasetImporter(config=dataset_config, metadata={}, name="dataset1", path="dataset1")
    run = RunImporter(config=dataset_config, metadata={}, name="run1", path="run1", parents={"dataset": dataset})
    parents = {"run": run, "dataset": dataset}
    return parents


@pytest.fixture
def source_config():
    source_config = {
        "literal": {"value": ["10.11"]},
        "parent_filters": {
            "include": {"run": []},
            "exclude": {"run": []},
        },
    }
    return source_config


def test_include_parents_with_single_value(dataset_config, parents, source_config):
    # Test filtering includes properly
    source_config["parent_filters"]["include"]["run"] = ["n1$"]
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 1

    # Test filtering excludes properly
    source_config["parent_filters"]["include"]["run"] = ["xxxxx"]
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 0


def test_include_parents_with_multiple_values(dataset_config, parents, source_config):
    # Test filtering includes properly
    source_config["parent_filters"]["include"]["run"] = ["^abc", "def", "n1$"]
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 1

    # Test filtering excludes properly
    source_config["parent_filters"]["include"]["run"] = ["xxxxx", "yyy"]
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 0


def test_exclude_parents_with_single_value(dataset_config, parents, source_config):
    # Test filtering excludes properly
    source_config["parent_filters"]["exclude"]["run"] = [
        "n1$",
    ]
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 0

    # Test filtering includes properly
    source_config["parent_filters"]["exclude"]["run"] = ["xxxxx"]
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 1


def test_exclude_parents_with_multiple_values(dataset_config, parents, source_config):
    # Test filtering excludes properly
    source_config["parent_filters"]["exclude"]["run"] = [
        "^abc",
        "def",
        "run1",
    ]
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 0

    # Test filtering includes properly
    source_config["parent_filters"]["exclude"]["run"] = ["xxxxx"]
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 1


def test_multi_parent_filters(dataset_config, parents, source_config):
    # Test filtering excludes properly
    source_config["parent_filters"]["exclude"] = {"run": ["aaaa", "n1$"]}  # excludes
    source_config["parent_filters"]["include"] = {"dataset": ["xxx"]}  # excludes
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 0

    source_config["parent_filters"]["exclude"] = {"dataset": ["aaaa", "t1$"]}  # excludes
    source_config["parent_filters"]["include"] = {"run": ["aaaa", "n1$"]}  # includes
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 0

    source_config["parent_filters"]["exclude"] = {"dataset": ["aaa"]}  # includes
    source_config["parent_filters"]["include"] = {"run": ["t1$"]}  # excludes
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 0

    # Test filtering includes properly
    source_config["parent_filters"]["exclude"] = {"run": ["t1$"]}  # includes
    source_config["parent_filters"]["include"] = {"dataset": ["t1$"]}  # includes
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 1

    source_config["parent_filters"]["include"] = {"dataset": ["t1$"]}  # includes
    source_config["parent_filters"]["exclude"] = {"run": ["xxx"]}  # includes
    finder = DefaultImporterFactory(source_config)
    items = finder.find(VoxelSpacingImporter, dataset_config, {}, **parents)
    assert len(items) == 1
