from importers.deposition import DepositionImporter
from importers.deposition_key_photo import DepositionKeyPhotoImporter
from mypy_boto3_s3 import S3Client

from common.fs import FileSystemApi
from tests.s3_import.test_depositions import validate_deposition_metadata
from tests.s3_import.util import create_config, list_dir


def test_key_photo_import_http(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
) -> None:
    output_prefix = "output"
    output_path = f"{test_output_bucket}/{output_prefix}"

    config = create_config(s3_fs, test_output_bucket, "depositions/deposition1.yaml")
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


def test_no_import_deposition_key_photo(
        s3_client: S3Client, s3_fs: FileSystemApi, test_output_bucket: str,
) -> None:
    config = create_config(s3_fs, test_output_bucket, "depositions/deposition1.yaml")
    deposition = list(DepositionImporter.finder(config))[0]
    for item in DepositionKeyPhotoImporter.finder(config, deposition=deposition):
        item.allow_imports = False
        item.import_item()
    deposition.import_metadata()
    deposition_dir = f"{test_output_bucket}/output/depositions_metadata/{deposition.name}/Images"
    assert list_dir(s3_client, test_output_bucket, deposition_dir) == []
