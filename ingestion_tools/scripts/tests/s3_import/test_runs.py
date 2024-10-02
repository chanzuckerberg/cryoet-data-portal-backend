import json

from importers.dataset import DatasetImporter
from importers.deposition import DepositionImporter
from importers.run import RunImporter
from importers.utils import IMPORTERS

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


def test_import_run_metadata(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    config_file = "tests/fixtures/dataset1.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    deposition = list(DepositionImporter.finder(config))[0]
    dataset = list(DatasetImporter.finder(config, deposition=deposition))[0]
    runs = list(RunImporter.finder(config, dataset=dataset, deposition=deposition))
    for run in runs:
        run.import_metadata()

    assert len(runs) == 2

    for run_name in ["TS_run1", "TS_run2"]:
        with s3_fs.open(f"{output_path}/10001/{run_name}/run_metadata.json", "r") as fh:
            output = fh.read()
        metadata = json.loads(output)
        assert metadata["run_name"] == run_name
        assert metadata["deposition_id"] == "10301"
