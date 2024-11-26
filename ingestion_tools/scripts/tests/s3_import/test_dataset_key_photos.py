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


@pytest.fixture
def ingestion_config(s3_fs: FileSystemApi, test_output_bucket: str) -> DepositionImportConfig:
    config_file = "tests/fixtures/dataset/keyphoto.yaml"
    output_prefix = "output"
    output_path = f"{test_output_bucket}/{output_prefix}"
    input_bucket = "test-public-bucket"
    return DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)


def get_parents(config: DepositionImportConfig) -> dict[str, BaseImporter]:
    parents = {"deposition": list(DepositionImporter.finder(config))[0]}
    parents["dataset"] = list(DatasetImporter.finder(config, **parents))[0]
    return parents


def set_dataset_keyphoto_sources(ingestion_config: DepositionImportConfig, value: dict[str, str]) -> None:
    if not value:
        return
    ingestion_config.object_configs["dataset_keyphoto"] = [{"sources": [{"literal": {"value": value}}]}]


@pytest.mark.parametrize(
    "keyphoto_source",
    [
        # valid http source in the ingestion config
        {
            "snapshot": "http://nginx:80/input_bucket/snapshot.gif",
            "thumbnail": "http://nginx:80/input_bucket/thumbnail.gif",
        },
        # valid s3 source in the ingestion config
        {
            "snapshot": "test-public-bucket/input_bucket/snapshot.gif",
            "thumbnail": "test-public-bucket/input_bucket/thumbnail.gif",
        },
    ],
)
def test_dataset_key_photo_import_from_valid_config_source(
    ingestion_config: DepositionImportConfig,
    test_output_bucket: str,
    s3_client: S3Client,
    keyphoto_source: dict[str, str],
) -> None:
    set_dataset_keyphoto_sources(ingestion_config, keyphoto_source)

    parents = get_parents(ingestion_config)
    key_photos = list(DatasetKeyPhotoImporter.finder(ingestion_config, **parents))
    for item in key_photos:
        item.import_item()

    # Check that the metadata is correct
    metadata = key_photos[0].get_metadata()
    # Check actual s3 files
    s3_files = get_children(s3_client, test_output_bucket, "output/10001/Images")
    assert len(metadata) == 2
    image_keys = {"snapshot", "thumbnail"}
    for key in image_keys:
        assert key in metadata
        assert metadata[key] == f"10001/Images/{key}.gif"
        assert f"{key}.gif" in s3_files


@pytest.mark.parametrize(
    "keyphoto_source",
    [
        # no source listed in the ingestion config
        None,
        # invalid http source in the ingestion config
        {
            "snapshot": "s3://input_bucket/invalid-snapshot.gif",
            "thumbnail": "s3://input_bucket/invalid-thumbnail.gif",
        },
        # invalid s3 source in the ingestion config
        {
            "snapshot": "http://nginx:80/input_bucket/invalid-snapshot.gif",
            "thumbnail": "http://nginx:80/input_bucket/invalid-thumbnail.gif",
        },
    ],
)
def test_dataset_key_photo_import_from_tomogram_keyphoto(
    ingestion_config: DepositionImportConfig,
    test_output_bucket: str,
    s3_client: S3Client,
    add_tomo_image: None,
    keyphoto_source: dict[str, str],
) -> None:
    set_dataset_keyphoto_sources(ingestion_config, keyphoto_source)

    parents = get_parents(ingestion_config)
    key_photos = list(DatasetKeyPhotoImporter.finder(ingestion_config, **parents))
    for item in key_photos:
        item.import_item()

    # Check that the metadata is correct
    metadata = key_photos[0].get_metadata()
    # Check actual s3 files
    s3_files = get_children(s3_client, test_output_bucket, "output/10001/Images")
    assert len(metadata) == 2
    image_keys = {"snapshot", "thumbnail"}
    for key in image_keys:
        assert key in metadata
        assert metadata[key] == f"10001/Images/{key}.png"
        assert f"{key}.png" in s3_files


# Raises runtime exception because no tomogram key photo exists
def test_dataset_key_photo_import_for_no_tomogram_keyphoto_exists(
    ingestion_config: DepositionImportConfig,
    test_output_bucket: str,
    s3_client: S3Client,
) -> None:
    parents = get_parents(ingestion_config)
    key_photos = list(DatasetKeyPhotoImporter.finder(ingestion_config, **parents))
    with pytest.raises(RuntimeError):
        for item in key_photos:
            item.import_item()

    # Check actual s3 files
    s3_files = get_children(s3_client, test_output_bucket, "output/10001/Images")
    assert len(s3_files) == 0
