import json
from sqlalchemy.exc import NoResultFound
import logging
import os
from datetime import datetime
from functools import lru_cache
from pathlib import PurePath
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from botocore.exceptions import ClientError
from database import models
from s3fs import S3FileSystem
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
else:
    S3Client = object

logger = logging.getLogger("config")


class DBImportConfig:
    s3_client: S3Client
    s3fs: S3FileSystem
    bucket_name: str
    s3_prefix: str
    https_prefix: str
    session: Session

    def __init__(
        self,
        s3_client: S3Client,
        s3fs: S3FileSystem,
        bucket_name: str,
        https_prefix: str,
        session: Session,
    ):
        self.s3_client = s3_client
        self.s3fs = s3fs
        self.bucket_name = bucket_name
        self.s3_prefix = f"s3://{bucket_name}"
        self.https_prefix = https_prefix if https_prefix else "https://files.cryoetdataportal.cziscience.com"
        self.session = session
        self.deposition_map: dict[int, models.Deposition] = {}

    def get_db_session(self) -> Session:
        return self.session

    def load_deposition_map(self) -> None:
        session = self.get_db_session()
        for item in session.scalars(sa.select(models.Deposition)).all():
            self.deposition_map[item.id] = item

    @lru_cache  # noqa
    def get_alignment_by_path(self, path: str) -> int | None:
        session = self.get_db_session()
        for item in session.scalars(
            sa.select(models.Alignment).where(models.Alignment.s3_alignment_metadata == path),
        ).all():
            return item.id

    @lru_cache  # noqa
    def get_tiltseries_by_path(self, path: str) -> int | None:
        session = self.get_db_session()
        # '_' is a wildcard character in sql LIKE queries, so we need to escape them!
        escaped_path = os.path.dirname(path).replace("_", "\\_")
        path = os.path.join(self.s3_prefix, escaped_path, "%")
        try:
            item = session.scalars(sa.select(models.Tiltseries).where(models.Tiltseries.s3_mrc_file.like(path))).one()
            return item.id
        except NoResultFound:
            # We have a few runs that (erroneously) are missing tiltseries.
            # They need to be fixed, but in the meantime let's not fail ingestion
            # for the entire dataset based on that problem.
            return None

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

    def recursive_glob_s3(self, prefix: str, glob_string: str) -> list[str]:
        # Returns path to a matched glob.
        s3 = self.s3fs
        prefix = prefix.rstrip("/")
        path = os.path.join(self.bucket_name, prefix, glob_string)
        logger.info("Recursively looking for files in %s", path)
        return s3.glob(path)

    def recursive_glob_prefix(self, prefix: str, glob_string: str) -> list[str]:
        # Returns a prefix that contains a given glob'd path but not the path to the found item itself.
        s3 = self.s3fs
        prefix = prefix.rstrip("/")
        path = os.path.join(self.bucket_name, prefix, glob_string)
        logger.info("Recursively looking for files in %s", path)
        return [os.path.dirname(item[len(self.bucket_name) + 1 :]) for item in s3.glob(path)]

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
            if key.startswith(self.bucket_name):
                key = key[len(self.bucket_name) + 1 :]
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
