import pytest
from importers.utils import IMPORTERS

from common.config import DepositionImportConfig
from common.fs import FileSystemApi


@pytest.mark.parametrize(
    "output_path",
    ["my-bucket/output", "my-bucket/output/", "s3://my-bucket/output", "s3://my-bucket/output/"],
)
def test_output_prefix_is_normalized(output_path: str) -> None:
    # The output may be a prefix inside a bucket, with or without the s3:// scheme and a trailing slash. S3 globs
    # return paths without the scheme, so metadata paths are only relative to the prefix if the scheme is dropped.
    fs = FileSystemApi.get_fs_api(mode="local", force_overwrite=False)
    config = DepositionImportConfig(fs, "tests/fixtures/dataset1.yaml", output_path, "test-public-bucket", IMPORTERS)
    assert config.output_prefix == "my-bucket/output"
    assert config.to_formatted_path("my-bucket/output/10001/RUN1/foo.mrc") == "10001/RUN1/foo.mrc"
