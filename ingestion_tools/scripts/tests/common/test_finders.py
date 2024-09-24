import json

import pytest
from importers.tiltseries import TiltSeriesImporter
from importers.utils import IMPORTERS
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.finders import DestinationFilteredMetadataFinder
from common.fs import FileSystemApi


@pytest.fixture
def run_name() -> str:
    return "random_run"


@pytest.fixture
def dataset_id() -> int:
    return 20000


@pytest.fixture(autouse=True)
def setup_data(test_output_bucket: str, s3_client: S3Client, run_name: str, dataset_id: int) -> None:
    def _put_data(prefix: int, data: dict):
        s3_client.put_object(
            Bucket=test_output_bucket,
            Key=f"{dataset_id}/{run_name}/TiltSeries/{prefix}-tiltseries_metadata.json",
            Body=json.dumps(data).encode("utf-8"),
        )

    _put_data(100, {"deposition_id": 300})
    _put_data(
        101,
        {"deposition_id": 301, "authors": [{"name": {"initial": "A", "last": "Smith"}}, {"name": {"first": "Bob"}}]},
    )


@pytest.fixture
def config(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
) -> DepositionImportConfig:
    import_config = "tests/fixtures/dataset1.yaml"
    return DepositionImportConfig(s3_fs, import_config, test_output_bucket, "test-public-bucket", IMPORTERS)


@pytest.mark.parametrize(
    "filters, expected_prefixes",
    [
        ([{"key": "non-existent-field-name", "value": 300}], []),
        ([{"key": "deposition_id", "value": 300}], [100]),
        ([{"key": ["authors", "name", "first"], "value": "Bob"}], [101]),
        ([{"key": ["authors", "name", "first"], "value": "Alice"}], []),
        ([{"key": ["invalid", "name", "first"], "value": "Bob"}], []),
        ([{"key": "deposition_id", "value": 303}], []),
        ([], [100, 101]),
    ],
)
def test_destination_filtered_metadata_finder(
    config: DepositionImportConfig,
    test_output_bucket: str,
    dataset_id: int,
    run_name: str,
    filters: list[dict],
    expected_prefixes: list[int],
):
    finder = DestinationFilteredMetadataFinder(filters, importer_cls=TiltSeriesImporter)
    actual_result = finder.find(config, {"dataset_name": dataset_id, "run_name": run_name})

    expected = {}
    for expected_prefix in expected_prefixes:
        expected_filename = (
            f"{test_output_bucket}/{dataset_id}/{run_name}/TiltSeries/{expected_prefix}-tiltseries_metadata.json"
        )
        expected[expected_filename] = expected_filename
    assert actual_result == expected
