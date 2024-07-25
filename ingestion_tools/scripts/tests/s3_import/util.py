from typing import List

from mypy_boto3_s3 import S3Client


def list_dir(s3_client: S3Client, bucket: str, prefix: str, assert_non_zero_size: bool = False) -> List[str]:
    files = s3_client.list_objects(Bucket=bucket, Prefix=prefix)
    if assert_non_zero_size:
        for item in files["Contents"]:
            assert item["Size"] > 0
    return [item["Key"] for item in files["Contents"]] if "Contents" in files else []
