import json

from importers.dataset import DatasetImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from importers.deposition import DepositionImporter
from importers.utils import IMPORTERS
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import list_dir


def test_import_dataset_metadata(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    """Test format_data with partially filled data."""
    config_file = "tests/fixtures/dataset1.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    deposition = list(DepositionImporter.finder(config))[0]
    dataset = list(DatasetImporter.finder(config, deposition=deposition))[0]
    dataset.import_metadata()

    with s3_fs.open(f"{output_path}/10001/dataset_metadata.json", "r") as fh:
        output = fh.read()
    metadata = json.loads(output)
    assert metadata["dataset_title"] == "Dataset 1"
    assert metadata["deposition_id"] == "10301"

    # Check that existing data is preserved
    assert metadata["cell_strain"]["name"] == "Strain 1"
    assert metadata["cell_strain"]["id"] == "CVCL_88888"
    assert metadata["organism"]["name"] == "Organism 1"
    assert metadata["cell_type"]["id"] == "CL:0000000"

    # Check that missing fields are filled with defaults
    assert metadata["organism"]["taxonomy_id"] == "not_reported"
    assert metadata["cell_type"]["name"] == "not_reported"

    # Check that missing keys are created with defaults
    for key in ["cell_component", "development_stage", "disease", "tissue"]:
        assert metadata[key]["name"] == "not_reported"
        assert metadata[key]["id"] == "not_reported"


def test_dataset_format_data_empty_input() -> None:
    """Test format_data with empty input dict."""
    data = {}
    result = DatasetImporter.format_data(data)

    expected_keys = [
        "assay", "cell_component", "cell_strain", "cell_type",
        "development_stage", "disease", "organism", "tissue",
    ]

    for key in expected_keys:
        assert key in result
        assert result[key]["name"] == "not_reported"
        if key == "organism":
            assert result[key]["taxonomy_id"] == "not_reported"
        else:
            assert result[key]["id"] == "not_reported"


def test_dataset_format_data_complete_data() -> None:
    data = {
        "assay": {"name": "assay_name", "id": "assay_id"},
        "cell_component": {"name": "component_name", "id": "component_id"},
        "cell_strain": {"name": "strain_name", "id": "strain_id"},
        "cell_type": {"name": "type_name", "id": "type_id"},
        "development_stage": {"name": "stage_name", "id": "stage_id"},
        "disease": {"name": "disease_name", "id": "disease_id"},
        "organism": {"name": "organism_name", "taxonomy_id": "12345"},
        "tissue": {"name": "tissue_name", "id": "tissue_id"},
    }
    result = DatasetImporter.format_data(data)

    # All original data should be preserved
    assert result == data


def test_no_import_dataset_metadata_and_key_photo(
    s3_fs: FileSystemApi, test_output_bucket: str, s3_client: S3Client,
) -> None:
    config_file = "tests/fixtures/dataset1.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    deposition = list(DepositionImporter.finder(config))[0]
    dataset = list(DatasetImporter.finder(config, deposition=deposition))[0]
    dataset.allow_imports = False
    keyphotos = DatasetKeyPhotoImporter.finder(config, dataset=dataset)
    for item in keyphotos:
        item.allow_imports = False
        item.import_item()
    dataset.import_metadata()

    actual = list_dir(s3_client, test_output_bucket, "output/10001/")
    assert actual == []
