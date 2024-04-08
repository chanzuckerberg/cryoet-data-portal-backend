import pytest
from importers.dataset import DatasetImporter
from importers.run import RunImporter
from importers.tomogram import TomogramImporter
from importers.voxel_spacing import VoxelSpacingImporter

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


@pytest.mark.parametrize(
    "import_config, expected",
    [
        # By default, we read voxel spacing from the import config file
        ("tests/fixtures/voxel_spacing/tomo_metadata.yaml", "1.123"),
        # Or we can read it from a data map.
        ("tests/fixtures/voxel_spacing/tomo_run_data_map.yaml", "4.568"),
        # Or we can use the "overrides" functionality to override it per run
        ("tests/fixtures/voxel_spacing/overrides_by_run.yaml", "5.679"),
        # Or if the import config leaves it empty, we can read it from the MRC headers
        ("tests/fixtures/voxel_spacing/mrc_header.yaml", "14.08"),
    ],
)  # type: ignore
def test_voxel_spacing_by_tomogram_metadata(
    s3_fs: FileSystemApi,
    test_output_bucket: str,
    import_config: str,
    expected: str,
) -> None:
    output_path = f"{test_output_bucket}/output"
    input_bucket = "test-public-bucket"

    config = DepositionImportConfig(s3_fs, import_config, output_path, input_bucket)
    config.load_map_files()

    datasets = config.find_datasets(DatasetImporter, None, s3_fs)
    runs = config.find_runs(RunImporter, datasets[0], s3_fs)
    voxel_spacings = config.find_voxel_spacings(VoxelSpacingImporter, runs[0], s3_fs)
    tomos = config.find_tomograms(TomogramImporter, voxel_spacings[0], s3_fs)

    assert voxel_spacings[0].name == "{:.3f}".format(round(float(expected), 3))

    # I'm not sure why numpy's returning weird 14.079999 like floats instead of 14.08
    assert round(tomos[0].get_voxel_spacing(), 4) == float(expected)
