import json
from os.path import basename

import ndjson
import pytest
from importers.annotation import AnnotationImporter, PointAnnotation
from importers.dataset import DatasetImporter
from importers.run import RunImporter
from importers.tomogram import TomogramImporter
from mypy_boto3_s3 import S3Client

from common.config import DepositionImportConfig
from common.fs import FileSystemApi
from common.metadata import AnnotationMetadata
from importers.voxel_spacing import VoxelSpacingImporter
from standardize_dirs import IMPORTERS

default_anno_metadata = {
    "annotation_object": {
        "id": "GO:0001234",
        "name": "some protein",
    },
    "dates": {
        "deposition_date": "2022-02-02",
        "release_date": "2022-02-02",
        "last_modified": "2022-02-02",
    },
    "annotation_method": "manual annotation",
    "method_type": "hybrid",
    "annotation_publications": "EMPIAR-12345",
    "ground_truth_status": True,
    "authors": [{"name": "Author 1", "ORCID": "0000-0000-0000-0000", "primary_author_status": True}],
    "annotation_software": "pyTOM + Keras",
    "version": "1.0",
    "is_curator_recommended": True,
}


@pytest.fixture
def dataset_config(s3_fs: FileSystemApi, test_output_bucket: str) -> DepositionImportConfig:
    config_file = "tests/fixtures/annotations/anno_config.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"
    config = DepositionImportConfig(s3_fs, config_file, output_path, input_bucket, IMPORTERS)
    return config


@pytest.fixture
def tomo_importer(dataset_config: DepositionImportConfig) -> TomogramImporter:
    dataset = DatasetImporter(config=dataset_config, metadata={}, name="dataset1", path="dataset1")
    run = RunImporter(config=dataset_config, metadata={}, name="00011", path="00011", parents={"dataset": dataset})
    vs = VoxelSpacingImporter(config=dataset_config, metadata={}, name="10.0", path="vs1", parents={"dataset": dataset, "run": run})
    tomo = TomogramImporter(config=dataset_config, metadata={}, name="tomo1", path="run1", parents={"dataset": dataset, "run": run, "voxel_spacing": vs})
    return tomo


def list_dir(s3_client: S3Client, bucket: str, prefix: str) -> None:
    files = s3_client.list_objects(Bucket=bucket, Prefix=prefix)
    fnames = []
    for item in files["Contents"]:
        fnames.append(item["Key"])
    return fnames


def test_import_annotation_metadata(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    tomo_importer: TomogramImporter,
    dataset_config: DepositionImportConfig,
    s3_client: S3Client,
) -> None:
    anno = PointAnnotation(
        config=dataset_config,
        metadata=default_anno_metadata,
        path="test-public-bucket/input_bucket/20002/annotations/points.csv",
        parents={"tomogram": tomo_importer, **tomo_importer.parents},
        identifier=100,
        columns="xyz",
        delimiter=",",
        file_format="csv",
    )
    anno.import_item()
    anno.import_metadata()

    # Strip the bucket name and annotation name from the annotation's output path.
    prefix = anno.get_output_path().rsplit("/", 1)[0].split("/", 1)[1]
    metadata_file = anno.get_output_path() + ".json"
    anno_file = anno.get_output_path() + "_point.ndjson"
    # Make sure we have a ndjson data file and a metadata file
    anno_files = [basename(item) for item in list_dir(s3_client, test_output_bucket, prefix)]
    assert "100-some_protein-1.0.json" in anno_files
    assert "100-some_protein-1.0_point.ndjson" in anno_files

    # Sanity check the metadata
    with s3_fs.open(metadata_file, "r") as fh:
        metadata = json.load(fh)
    assert metadata["annotation_object"] == default_anno_metadata["annotation_object"]
    assert metadata["annotation_software"] == default_anno_metadata["annotation_software"]
    assert metadata["object_count"] == 3
    fileinfo = metadata["files"][0]
    assert fileinfo["format"] == "ndjson"
    assert fileinfo["shape"] == "Point"
    assert "100-some_protein-1.0_point.ndjson" in fileinfo["path"]

    # Sanity check the ndjson file
    with s3_fs.open(anno_file, "r") as fh:
        points = ndjson.load(fh)
    assert len(points) == 3
