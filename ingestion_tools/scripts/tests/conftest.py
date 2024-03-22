import os
import random
import string
from typing import Any, Generator

import boto3
import pytest
from botocore.client import Config
from mypy_boto3_s3 import S3Client

from common.fs import FileSystemApi


@pytest.fixture
def endpoint_url() -> str:
    return os.getenv("ENDPOINT_URL", "http://motoserver:4000")


@pytest.fixture
def http_prefix() -> str:
    return "https://foo.com"


@pytest.fixture
def local_fs() -> FileSystemApi:
    return FileSystemApi.get_fs_api(mode="local", force_overwrite=False)


@pytest.fixture
def s3_fs(endpoint_url: str) -> FileSystemApi:
    return FileSystemApi.get_fs_api(
        mode="s3",
        force_overwrite=False,
        client_kwargs={"endpoint_url": endpoint_url},
    )


@pytest.fixture
def random_bucket_name() -> str:
    res = "".join(random.choices(string.ascii_lowercase, k=15))
    return res


@pytest.fixture
def test_output_bucket(s3_client: S3Client, random_bucket_name: str) -> Generator[str, Any, Any]:
    bucket_name = random_bucket_name
    s3_client.create_bucket(Bucket=bucket_name)
    yield bucket_name
    try:
        objects = s3_client.list_objects_v2(Bucket=bucket_name)["Contents"]
        objects = [{"Key": x["Key"]} for x in objects]
        s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})
    except KeyError:
        # We may not have written any files and that's ok.
        pass
    s3_client.delete_bucket(Bucket=bucket_name)


@pytest.fixture
def s3_client(endpoint_url: str) -> S3Client:
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        config=Config(signature_version="s3v4"),
    )
