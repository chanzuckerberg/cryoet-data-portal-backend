import boto3
import pytest
import string
import random
from botocore.client import Config
from common.fs import FileSystemApi
from mypy_boto3_s3 import S3Client
from typing import Generator, Any

@pytest.fixture
def local_fs() -> FileSystemApi:
    fs = FileSystemApi.get_fs_api(mode="local", force_overwrite=False)
    return fs

@pytest.fixture
def s3_fs() -> FileSystemApi:
    fs = FileSystemApi.get_fs_api(mode="s3", force_overwrite=False, client_kwargs={'endpoint_url': "http://motoserver:4000"})
    return fs

@pytest.fixture
def random_bucket_name() -> str:
    res = ''.join(random.choices(string.ascii_lowercase, k=15))
    return res

@pytest.fixture
def test_output_bucket(s3_client: S3Client, random_bucket_name: str) -> Generator[str, Any, Any]:
    bucket_name = random_bucket_name
    s3_client.create_bucket(
        Bucket=bucket_name
    )
    yield bucket_name
    try:
        objects = s3_client.list_objects_v2(Bucket = bucket_name)["Contents"]
        objects = list(map(lambda x: {"Key":x["Key"]},objects))
        s3_client.delete_objects(Bucket=bucket_name, Delete = {"Objects":objects})
    except KeyError:
        # We may not have written any files and that's ok.
        pass
    s3_client.delete_bucket(Bucket=bucket_name)


@pytest.fixture
def s3_client() -> S3Client:
    return boto3.client(
        "s3",
        endpoint_url="http://motoserver:4000",
        config=Config(signature_version="s3v4"),
    )
