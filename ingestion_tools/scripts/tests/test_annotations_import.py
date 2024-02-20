import json
import pytest

from common.config import DataImportConfig
from common.fs import FileSystemApi
from importers.dataset import DatasetImporter
from importers.tomogram import TomogramImporter
from importers.run import RunImporter
from importers.annotation import AnnotationImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from common.metadata import AnnotationMetadata
from mypy_boto3_s3 import S3Client

default_anno_metadata = {
  "annotation_object": {
    "id": "GO:0005835",
    "name": "fatty acid synthase complex",
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
def dataset_config(s3_fs: FileSystemApi, test_output_bucket: str) -> DataImportConfig:
    config_file = "tests/fixtures/annotations/anno_config.yaml"
    output_path = f"{test_output_bucket}/output"
    input_bucket = "input_bucket"
    config = DataImportConfig(s3_fs, config_file, output_path, input_bucket)
    return config

@pytest.fixture
def tomo_importer(dataset_config: DataImportConfig) -> TomogramImporter:
    dataset = DatasetImporter(dataset_config, None)
    run = RunImporter(config=dataset_config, parent=dataset, path="run1")
    tomo = TomogramImporter(config=dataset_config, parent=run, path="run1")
    return tomo

def test_import_annotation_metadata(s3_fs: FileSystemApi, test_output_bucket: str, tomo_importer: TomogramImporter, dataset_config: DataImportConfig) -> None:
    anno_config = {
      "metadata": default_anno_metadata,
      "sources": [{
        "columns": "xyz",
        "file_format": "csv",
        "glob_string": "annotations/points.csv",
        "shape": "Point",
        "is_visualization_default": False,
      }]
    }
    anno_metadata = AnnotationMetadata(dataset_config.fs, anno_config["metadata"])
    anno = AnnotationImporter(
        identifier="100",
        config=dataset_config,
        parent=tomo_importer,
        annotation_metadata=anno_metadata,
        annotation_config=anno_config,
    )
    anno.import_annotations(True)
    anno.import_metadata()