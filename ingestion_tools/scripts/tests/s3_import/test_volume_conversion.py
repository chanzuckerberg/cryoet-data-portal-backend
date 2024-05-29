import mrcfile

from common.fs import FileSystemApi
from common.image import make_pyramids


def test_convert_mrc_to_pyramid(s3_fs: FileSystemApi, test_output_bucket: str) -> None:
    output_path = f"{test_output_bucket}/output"
    print(output_path)
    input_file = "test-public-bucket/input_bucket/sample_tomos/input_mrc.mrc"
    make_pyramids(s3_fs, output_path, input_file)

    output_mrc = s3_fs.localreadable(output_path)
    mrc = mrcfile.open(output_mrc, "r")
    assert mrc.voxel_spacing.y == 14.08
