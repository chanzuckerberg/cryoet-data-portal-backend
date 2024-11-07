
import numpy
import pytest
from importers.dataset import DatasetImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from importers.deposition import DepositionImporter
from importers.utils import IMPORTERS
from mypy_boto3_s3 import S3Client
from PIL import Image

from common.config import BaseImporter, DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import get_children


@pytest.fixture
def add_tomo_image(s3_client: S3Client, test_output_bucket: str) -> None:
    for image_format in ["snapshot", "thumbnail"]:
        path = f"output/10001/TS_run1/Reconstructions/VoxelSpacing13.480/Images/100/key-photo-{image_format}.png"
        imarray = numpy.random.rand(20, 20, 3) * 255
        im = Image.fromarray(imarray.astype("uint8")).convert("RGBA")
        s3_client.put_object(Bucket=test_output_bucket, Key=path, Body=im.tobytes())


def get_parents(config: DepositionImportConfig) -> dict[str, BaseImporter]:
    parents = {"deposition": list(DepositionImporter.finder(config))[0]}
    parents["dataset"] = list(DatasetImporter.finder(config, **parents))[0]
    return parents


def test_key_photo_import_http(s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client) -> None:
    config_file = "tests/fixtures/dataset1.yaml"
    output_prefix = "output"
    output_path = f"{test_output_bucket}/{output_prefix}"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    key_photos = list(DatasetKeyPhotoImporter.finder(config, **get_parents(config)))

    for item in key_photos:
        item.import_item()

    # Check that the metadata is correct
    metadata = key_photos[0].get_metadata()
    # Check actual s3 files
    s3_files = get_children(s3_client, test_output_bucket, f"{output_prefix}/10001/Images")
    assert len(metadata) == 2
    image_keys = {"snapshot", "thumbnail"}
    for key in image_keys:
        assert key in metadata
        assert metadata[key] == f"10001/Images/{key}.png"
        assert f"{key}.png" in s3_files


def test_key_photo_import_from_tomogram(
    s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client, add_tomo_image: None,
) -> None:
    config_file = "tests/fixtures/dataset2.yaml"
    output_prefix = "output"
    output_path = f"{test_output_bucket}/{output_prefix}"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    key_photos = list(DatasetKeyPhotoImporter.finder(config, **get_parents(config)))

    for item in key_photos:
        item.import_item()

    # Check that the metadata is correct
    metadata = key_photos[0].get_metadata()
    # Check actual s3 files
    s3_files = get_children(s3_client, test_output_bucket, f"{output_prefix}/10001/Images")
    assert len(metadata) == 2
    image_keys = {"snapshot", "thumbnail"}
    for key in image_keys:
        assert key in metadata
        assert metadata[key] == f"10001/Images/{key}.png"
        assert f"{key}.png" in s3_files
