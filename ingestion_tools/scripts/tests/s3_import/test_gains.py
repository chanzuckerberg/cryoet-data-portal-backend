from os.path import basename

from importers.dataset import DatasetImporter
from importers.gain import GainImporter
from importers.run import RunImporter
from mypy_boto3_s3 import S3Client
from standardize_dirs import IMPORTERS
from tests.s3_import.test_annotations_import import list_dir

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


def test_non_dm4_gains_import(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    s3_client: S3Client,
) -> None:
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    import_config = "tests/fixtures/dataset1.yaml"

    config = DepositionImportConfig(s3_fs, import_config, output_path, input_bucket, IMPORTERS)
    datasets = list(DatasetImporter.finder(config))
    runs = list(RunImporter.finder(config, dataset=datasets[0]))
    gains = list(GainImporter.finder(config, dataset=datasets[0], run=runs[0]))
    for gain in gains:
        gain.import_item()

    dataset_name = datasets[0].name
    run_name = runs[0].name
    prefix = f"output/{dataset_name}/{run_name}/Frames"
    gain_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert f"{run_name}_gain.gain" in gain_files
