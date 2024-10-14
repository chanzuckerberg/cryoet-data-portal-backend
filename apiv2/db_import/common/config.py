import json
import logging
from datetime import datetime
from pathlib import PurePath
from typing import TYPE_CHECKING, Any

from botocore.exceptions import ClientError
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
else:
    S3Client = object

logger = logging.getLogger("config")


class DBImportConfig:
    s3_client: S3Client
    bucket_name: str
    s3_prefix: str
    https_prefix: str
    session: Session

    def __init__(
        self,
        s3_client: S3Client,
        bucket_name: str,
        https_prefix: str,
        session: Session,
    ):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.s3_prefix = f"s3://{bucket_name}"
        self.https_prefix = https_prefix if https_prefix else "https://files.cryoetdataportal.cziscience.com"
        self.session = session

    def get_db_session(self) -> Session:
        return self.session

    def find_subdirs_with_files(self, prefix: str, target_filename: str) -> list[str]:
        paginator = self.s3_client.get_paginator("list_objects_v2")
        logger.info("looking for prefix %s", prefix)
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter="/")
        result = []
        for page in pages:
            for obj in page.get("CommonPrefixes", []):
                try:
                    subdir = obj["Prefix"]
                    self.s3_client.head_object(Bucket=self.bucket_name, Key=f"{subdir}{target_filename}")
                    result.append(subdir)
                except Exception:
                    continue
        return result

    def glob_s3(self, prefix: str, glob_string: str, is_file: bool = True):
        paginator = self.s3_client.get_paginator("list_objects_v2")
        if prefix.startswith("s3://"):
            prefix = "/".join(prefix.split("/")[3:])
        logger.info("looking for prefix %s%s", prefix, glob_string)
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter="/")
        page_key = "Contents" if is_file else "CommonPrefixes"
        obj_key = "Key" if is_file else "Prefix"
        for page in pages:
            for obj in page.get(page_key, {}):
                if not obj:
                    break
                if PurePath(obj[obj_key]).match(glob_string):
                    yield obj[obj_key]

    def load_key_json(self, key: str, is_file_required: bool = True) -> dict[str, Any] | None:
        """
        Loads file matching the key value as json. If file does not exist, will raise error if is_file_required is True
        else it will return None.
        """
        try:
            text = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return json.loads(text["Body"].read())
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "NoSuchKey" and not is_file_required:
                logger.warning("NoSuchKey on bucket_name=%s key=%s", self.bucket_name, key)
                return None
            else:
                raise


def map_to_value(db_key: str, mapping: dict[str, Any], data: dict[str, Any]) -> Any:
    """
    For a key, it maps to value by traversing the json as specified in the mapping parameter or returns the precomputed
    value if mapping has a non list value.
    """
    data_path = mapping.get(db_key)
    if not isinstance(data_path, list):
        return data_path

    value = None
    for path_part in data_path:
        value = data.get(path_part) if not value else value.get(path_part)
        if not value:
            break
    if value and "date" in db_key:
        value = datetime.strptime(value, "%Y-%m-%d")  # type: ignore
    return value
