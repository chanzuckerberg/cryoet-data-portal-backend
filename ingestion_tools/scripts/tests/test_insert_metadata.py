import json

from common.config import DataImportConfig
from importers.dataset import DatasetImporter


def test_import_dataset_metadata(s3_fs, test_output_bucket):
    config_file = "tests/fixtures/dataset1.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "input_bucket"
    config = DataImportConfig(s3_fs, config_file, output_path, input_bucket)
    dataset = DatasetImporter(config, None)
    dataset.import_metadata(output_path)

    output = s3_fs.open(f"{output_path}/10001/dataset_metadata.json", "r").read()
    metadata = json.loads(output)
    assert metadata["dataset_title"] == "Dataset 1"
