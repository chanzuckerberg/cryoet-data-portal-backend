import pytest

from common.config import DataImportConfig
from importers.dataset import DatasetImporter
from importers.run import RunImporter
from importers.tomogram import TomogramImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from common.fs import FileSystemApi
from mypy_boto3_s3 import S3Client

@pytest.mark.parametrize('import_config, expected', [
    # By default, we read voxel spacing from the import config file
    ("tests/fixtures/voxel_spacing/tomo_metadata.yaml", "1.1234"),
    # Or we can read it from a data map.
    ("tests/fixtures/voxel_spacing/tomo_run_data_map.yaml", "4.5678"),
    # Or we can use the "overrides" functionality to override it per run
    ("tests/fixtures/voxel_spacing/overrides_by_run.yaml", "5.6789"),
    # Or if the import config leaves it empty, we can read it from the MRC headers
    ("tests/fixtures/voxel_spacing/mrc_header.yaml", "14.08"),
]) # type: ignore
def test_voxel_spacing_by_tomogram_metadata(s3_fs: FileSystemApi, test_output_bucket: str, import_config: str, expected: str) -> None:
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"

    config = DataImportConfig(s3_fs, import_config, output_path, input_bucket)
    config.load_map_files()
    dataset = DatasetImporter(config, None)
    run =  RunImporter.find_runs(config, dataset)[0]
    tomo = TomogramImporter.find_tomograms(config, run, skip_cache=True)[0]
    run.set_voxel_spacing(tomo.get_voxel_spacing())

    assert run.voxel_spacing == '{:.3f}'.format(round(float(expected), 3))

    # I'm not sure why numpy's returning weird 14.079999 like floats instead of 14.08
    assert round(tomo.get_voxel_spacing(), 4) == float(expected)