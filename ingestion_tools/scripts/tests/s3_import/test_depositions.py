import json

from importers.deposition import DepositionImporter
from mypy_boto3_s3 import S3Client

from common.fs import FileSystemApi
from tests.s3_import.util import create_config, list_dir


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
) -> None:
    output_path = f"{test_output_bucket}/output"
    config = create_config(s3_fs, test_output_bucket, "depositions/deposition1.yaml")
    deposition = list(DepositionImporter.finder(config))[0]
    deposition.import_metadata()
    validate_deposition_metadata(s3_fs, output_path)


def test_invalid_deposition_metadata_import(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    config = create_config(s3_fs, test_output_bucket, "depositions/deposition2.yaml")
    deposition = list(DepositionImporter.finder(config))[0]
    deposition.import_metadata()
    assert s3_fs.glob(f"{output_path}/depositions_metadata/10302/deposition_metadata.json") == []


def test_no_import_deposition_metadata(
        s3_client: S3Client, s3_fs: FileSystemApi, test_output_bucket: str,
) -> None:
    config = create_config(s3_fs, test_output_bucket, "depositions/deposition1.yaml")
    deposition = list(DepositionImporter.finder(config))[0]
    deposition.allow_imports = False
    deposition.import_metadata()
    deposition_dir = f"{test_output_bucket}/output/depositions_metadata/{deposition.name}"
    assert list_dir(s3_client, test_output_bucket, deposition_dir) == []
