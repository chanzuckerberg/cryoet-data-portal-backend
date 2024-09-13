import json
import os
from typing import Any, Callable

import pytest as pytest
from importers.db.base_importer import S3Client
from standardize_dirs import IMPORTERS

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from common.id_helper import IdentifierHelper
from tests.s3_import.test_alignments import get_parents


class FooIdentifierHelper(IdentifierHelper):
    @classmethod
    def _get_container_key(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        return parents["run"].name

    @classmethod
    def _get_metadata_glob(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        run = parents["run"]
        return os.path.join(run.get_output_path(), "*foo_metadata.json")

    @classmethod
    def _generate_hash_key(
        cls,
        container_key: str,
        metadata: dict[str, Any],
        parents: dict[str, Any],
        *args,
        **kwargs,
    ) -> str:
        return "-".join([container_key, str(metadata.get("foo_id"))])


@pytest.fixture
def add_foo_metadata(s3_client: S3Client, test_output_bucket: str) -> Callable[[str, int], None]:
    def _add_metadata(prefix: str, foo_id: int) -> None:
        body = json.dumps({"foo_id": foo_id}).encode("utf-8")
        s3_client.put_object(Bucket=test_output_bucket, Key=f"{prefix}100-foo_metadata.json", Body=body)

    return _add_metadata


@pytest.fixture
def config(s3_fs: FileSystemApi, test_output_bucket: str) -> DepositionImportConfig:
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    import_config = "tests/fixtures/dataset1.yaml"
    return DepositionImportConfig(s3_fs, import_config, output_path, input_bucket, IMPORTERS)


def reset_trackers():
    # Reset the global variables in IdentifierHelper to avoid side effects between tests
    FooIdentifierHelper.loaded_containers.clear()
    FooIdentifierHelper.cached_identifiers.clear()
    FooIdentifierHelper.next_identifier.clear()


@pytest.mark.parametrize(
    "existing_foo_id, expected_id",
    [
        (None, 100),  # No entry exists
        (2, 101),  # entry exists for a different key
        (1, 100),  # entry exists for a same key as test
    ],
)
def test_identifier_generation(
    config: DepositionImportConfig,
    add_foo_metadata: Callable[[str, int], None],
    existing_foo_id: int,
    expected_id: int,
) -> None:
    parents = get_parents(config)
    dataset_name = parents.get("dataset").name
    run_name = parents.get("run").name
    prefix = f"output/{dataset_name}/{run_name}/"
    if existing_foo_id:
        add_foo_metadata(prefix, existing_foo_id)

    reset_trackers()
    actual = FooIdentifierHelper.get_identifier(config, {"foo_id": 1}, parents)
    assert expected_id == actual
