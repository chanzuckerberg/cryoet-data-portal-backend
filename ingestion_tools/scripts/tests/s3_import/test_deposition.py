import json
from typing import Callable

import pytest as pytest
from importers.deposition import DepositionImporter
from importers.deposition_key_photo import DepositionKeyPhotoImporter
from mypy_boto3_s3 import S3Client
from standardize_dirs import IMPORTERS
from tests.s3_import.util import list_dir

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


@pytest.fixture
def create_config(s3_fs: FileSystemApi, test_output_bucket: str) -> Callable[[str], DepositionImportConfig]:
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    return lambda import_config: DepositionImportConfig(s3_fs, import_config, output_path, input_bucket, IMPORTERS)


def validate_deposition_metadata(s3_fs: FileSystemApi, output_path: str) -> dict[str, str]:
    with s3_fs.open(f"{output_path}/depositions_metadata/10301/deposition_metadata.json", "r") as fh:
        output = fh.read()
    metadata = json.loads(output)
    assert metadata["deposition_title"] == "Deposition 1"
    assert metadata["deposition_identifier"] == 10301
    assert metadata["deposition_description"] == "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed"
    return metadata


def test_import_deposition_metadata(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    create_config: Callable[[str], DepositionImportConfig],
) -> None:
    output_path = f"{test_output_bucket}/output"
    config = create_config("tests/fixtures/depositions/deposition1.yaml")
    deposition = list(DepositionImporter.finder(config))[0]
    deposition.import_metadata()
    validate_deposition_metadata(s3_fs, output_path)


def test_invalid_deposition_metadata_import(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    create_config: Callable[[str], DepositionImportConfig],
) -> None:
    output_path = f"{test_output_bucket}/output"
    config = create_config("tests/fixtures/depositions/deposition2.yaml")
    deposition = list(DepositionImporter.finder(config))[0]
    deposition.import_metadata()
    assert s3_fs.glob(f"{output_path}/depositions_metadata/10302/deposition_metadata.json") == []


def test_key_photo_import_http(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
    create_config: Callable[[str], DepositionImportConfig],
) -> None:
    output_prefix = "output"
    output_path = f"{test_output_bucket}/{output_prefix}"

    config = create_config("tests/fixtures/depositions/deposition1.yaml")
    deposition = list(DepositionImporter.finder(config))[0]
    for item in DepositionKeyPhotoImporter.finder(config, deposition=deposition):
        item.import_item()
    deposition.import_metadata()

    metadata = validate_deposition_metadata(s3_fs, output_path)
    deposition_path = f"depositions_metadata/{deposition.name}"
    s3_files = list_dir(
        s3_client,
        test_output_bucket,
        f"{output_prefix}/{deposition_path}/Images",
        assert_non_zero_size=True,
    )

    # Make sure the files are in our metadata and match our s3 file paths
    for key, path in metadata["key_photos"].items():
        assert key in ["snapshot", "thumbnail"]
        assert path.startswith(f"{deposition_path}/Images/")
        assert f"{output_prefix}/{path}" in s3_files
    assert len(metadata["key_photos"]) == 2
