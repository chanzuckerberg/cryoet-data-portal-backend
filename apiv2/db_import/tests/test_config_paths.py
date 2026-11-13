"""Path handling of DBImportConfig for data at a bucket root and at a prefix inside a bucket. Needs no S3 or db."""

import pytest
from db_import.common.config import PROD_URL, STAGING_URL, DBImportConfig
from db_import.importers.tomogram import TomogramItem


def make_config(bucket_path: str, https_prefix: str = "https://foo.com") -> DBImportConfig:
    return DBImportConfig(None, None, bucket_path, https_prefix, None)


@pytest.mark.parametrize(
    "bucket_path, bucket, root_prefix",
    [
        ("my-bucket", "my-bucket", ""),
        ("my-bucket/", "my-bucket", ""),
        ("s3://my-bucket", "my-bucket", ""),
        ("my-bucket/a/b", "my-bucket", "a/b"),
        ("my-bucket/a/b/", "my-bucket", "a/b"),
        ("s3://my-bucket/a/b/", "my-bucket", "a/b"),
    ],
)
def test_split_bucket_path(bucket_path: str, bucket: str, root_prefix: str) -> None:
    assert DBImportConfig.split_bucket_path(bucket_path) == (bucket, root_prefix)
    config = make_config(bucket_path)
    assert config.bucket_name == bucket
    assert config.root_prefix == root_prefix


def test_bucket_root_paths() -> None:
    # Importing from the bucket root must produce the same values as before prefixes were supported.
    config = make_config("my-bucket")
    assert config.data_root == "my-bucket"
    assert config.s3_prefix == "s3://my-bucket"
    assert config.relative("10001/RUN1/") == "10001/RUN1/"
    assert config.relative("my-bucket/10001/RUN1") == "10001/RUN1"
    assert config.relative("s3://my-bucket/10001/RUN1/") == "10001/RUN1/"
    assert config.key("10001/RUN1/") == "10001/RUN1/"
    assert config.key("") == ""
    assert config.from_key("10001/RUN1/") == "10001/RUN1/"
    assert config.fs_path("10001/RUN1") == "my-bucket/10001/RUN1"


def test_prefix_paths() -> None:
    config = make_config("s3://my-bucket/a/b/", "https://foo.com/a/b")
    assert config.data_root == "my-bucket/a/b"
    assert config.s3_prefix == "s3://my-bucket/a/b"
    # Metadata paths are relative to the data root, listings and db urls are fully qualified.
    assert config.relative("10001/RUN1/") == "10001/RUN1/"
    assert config.relative("my-bucket/a/b/10001/RUN1") == "10001/RUN1"
    assert config.relative("s3://my-bucket/a/b/10001/RUN1/") == "10001/RUN1/"
    assert config.relative("s3://my-bucket/a/b") == ""
    # Older metadata wrote "bucket/<path relative to the data root>".
    assert config.relative("my-bucket/10001/RUN1") == "10001/RUN1"
    # A bare root-prefix component is not stripped, since it can't be told apart from a root-relative path.
    assert config.relative("a/b/10001") == "a/b/10001"
    assert config.key("10001/RUN1/") == "a/b/10001/RUN1/"
    assert config.key("") == "a/b/"
    assert config.from_key("a/b/10001/RUN1/") == "10001/RUN1/"
    assert config.from_key(config.key("depositions_metadata/300/")) == "depositions_metadata/300/"
    assert config.fs_path("10001/RUN1") == "my-bucket/a/b/10001/RUN1"


def test_https_prefix_warning(caplog: pytest.LogCaptureFixture) -> None:
    make_config("my-bucket/a/b", "https://foo.com/a/b/")
    assert "does not end with" not in caplog.text
    make_config("my-bucket/a/b", "https://foo.com")
    assert "does not end with a/b" in caplog.text


def ng_config(base_url: str) -> str:
    return f'{{"layers": [{{"source": "zarr://{base_url}/10001/RUN1/Tomograms/100/foo.zarr"}}]}}'


@pytest.mark.parametrize(
    "bucket_path, https_prefix, written_url, expected_url",
    [
        # Bucket root: the production url is swapped for the staging url in staging only.
        ("my-bucket", STAGING_URL, PROD_URL, STAGING_URL),
        ("my-bucket", PROD_URL, PROD_URL, PROD_URL),
        ("my-bucket", "https://foo.com", PROD_URL, PROD_URL),
        # Prefix: urls of the bucket root, or already of the prefix, point at the https prefix of the import.
        ("my-bucket/a/b", f"{STAGING_URL}/a/b", PROD_URL, f"{STAGING_URL}/a/b"),
        ("my-bucket/a/b", f"{STAGING_URL}/a/b", STAGING_URL, f"{STAGING_URL}/a/b"),
        ("my-bucket/a/b", f"{STAGING_URL}/a/b", f"{STAGING_URL}/a/b", f"{STAGING_URL}/a/b"),
        ("my-bucket/a/b", f"{STAGING_URL}/a/b", f"{PROD_URL}/a/b", f"{STAGING_URL}/a/b"),
        ("my-bucket/a/b", f"{PROD_URL}/a/b/", PROD_URL, f"{PROD_URL}/a/b"),
        ("my-bucket/a/b", "https://foo.com/a/b", "https://other.com", "https://other.com"),
    ],
)
def test_update_ng_urls(bucket_path: str, https_prefix: str, written_url: str, expected_url: str) -> None:
    item = TomogramItem(make_config(bucket_path, https_prefix), {})
    assert item._update_ng_urls(ng_config(written_url)) == ng_config(expected_url)
