import json
from os.path import basename
from typing import Callable

import pandas as pd
import pytest
from importers.alignment import AlignmentImporter
from importers.base_importer import BaseImporter
from importers.dataset import DatasetImporter
from importers.deposition import DepositionImporter
from importers.run import RunImporter
from mypy_boto3_s3 import S3Client
from standardize_dirs import IMPORTERS

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from tests.s3_import.util import list_dir


@pytest.fixture
def input_bucket() -> str:
    return "test-public-bucket"


@pytest.fixture
def parents(config: DepositionImportConfig) -> dict[str, BaseImporter]:
    depositions = list(DepositionImporter.finder(config))
    datasets = list(DatasetImporter.finder(config, deposition=depositions[0]))
    runs = list(RunImporter.finder(config, dataset=datasets[0]))
    return {
        "deposition": depositions[0],
        "dataset": datasets[0],
        "run": runs[0],
    }


def add_alignment_metadata(s3_client: S3Client, test_output_bucket: str, prefix: str, deposition_id: int) -> None:
    body = json.dumps({"deposition_id": deposition_id}).encode("utf-8")
    s3_client.put_object(Bucket=test_output_bucket, Key=f"{prefix}100-alignment_metadata.json", Body=body)


@pytest.fixture
def validate_dataframe(
    input_bucket: str, test_output_bucket: str, s3_client: S3Client,
) -> Callable[[str, str, int], None]:
    def get_data_frame(bucket_name: str, path: str) -> pd.DataFrame:
        body = s3_client.get_object(Bucket=bucket_name, Key=path)["Body"]
        return pd.read_csv(body, sep=r"\s+")

    def validate(prefix: str, filename: str, id_prefix: int) -> None:
        alignment_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
        assert f"{id_prefix}-{filename}" in alignment_files
        actual = get_data_frame(input_bucket, f"input_bucket/10001_input/alignment/{filename}")
        expected = get_data_frame(test_output_bucket, f"{prefix}{id_prefix}-{filename}")
        assert actual.equals(expected)

    return validate


@pytest.fixture
def config(s3_fs: FileSystemApi, test_output_bucket: str, input_bucket: str) -> DepositionImportConfig:
    output_path = f"{test_output_bucket}/output"
    import_config = "tests/fixtures/dataset1.yaml"
    return DepositionImportConfig(s3_fs, import_config, output_path, input_bucket, IMPORTERS)


@pytest.mark.parametrize(
    "deposition_id, id_prefix",
    [
        (None, 100),  # No alignment metadata exists
        (100001, 101),  # alignment metadata exists for a different deposition
        (10301, 100),  # alignment metadata exists for the same deposition as test
    ],
)
def test_tlt_import(
    config: DepositionImportConfig,
    test_output_bucket: str,
    parents: dict[str, BaseImporter],
    validate_dataframe: Callable[[str, str, int], None],
    s3_client: S3Client,
    deposition_id: int,
    id_prefix: int,
) -> None:
    dataset_name = parents.get("dataset").name
    run_name = parents.get("run").name
    prefix = f"output/{dataset_name}/{run_name}/Alignments/"
    if deposition_id:
        add_alignment_metadata(s3_client, test_output_bucket, prefix, deposition_id)

    from importers.tilt import TiltImporter

    tilts = list(TiltImporter.finder(config, **parents))
    for tilt in tilts:
        tilt.import_item()

    validate_dataframe(prefix, "TS_run1.tlt", id_prefix)
    validate_dataframe(prefix, "TS_run1.xtilt", id_prefix)


@pytest.mark.parametrize(
    "deposition_id, id_prefix",
    [
        (None, 100),  # No alignment metadata exists
        (100001, 101),  # alignment metadata exists for a different deposition
        (10301, 100),  # alignment metadata exists for the same deposition as test
    ],
)
def test_alignment_imports(
    config: DepositionImportConfig,
    test_output_bucket: str,
    parents: dict[str, BaseImporter],
    validate_dataframe: Callable[[str, str, int], None],
    s3_client: S3Client,
    deposition_id: int,
    id_prefix: int,
) -> None:
    dataset_name = parents.get("dataset").name
    run_name = parents.get("run").name
    prefix = f"output/{dataset_name}/{run_name}/Alignments/"
    if deposition_id:
        add_alignment_metadata(s3_client, test_output_bucket, prefix, deposition_id)

    alignments = list(AlignmentImporter.finder(config, **parents))
    for alignment in alignments:
        alignment.import_item()

    validate_dataframe(prefix, "TS_run1.xf", id_prefix)
