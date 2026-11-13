import json
import logging
import os
from datetime import datetime
from functools import lru_cache
from pathlib import PurePath
from typing import TYPE_CHECKING, Any, Final

import sqlalchemy as sa
from botocore.exceptions import ClientError
from database import models
from s3fs import S3FileSystem
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
else:
    S3Client = object

logger = logging.getLogger("config")

STAGING_URL: Final[str] = "https://files.cryoet.staging.si.czi.technology"
PROD_URL: Final[str] = "https://files.cryoetdataportal.cziscience.com"


class DBImportConfig:
    """
    Paths passed around the importers are either relative to the data root (as stored in the metadata files,
    e.g. "10001/RUN1/...") or fully qualified ("bucket/..." or "s3://bucket/..."). `relative()` normalizes both to
    root-relative paths, `key()` / `fs_path()` turn those into S3 keys / s3fs paths.
    """

    s3_client: S3Client
    s3fs: S3FileSystem
    # Name of the bucket only, without the root prefix.
    bucket_name: str
    # Key prefix inside the bucket that holds the data ("" when the data is at the bucket root).
    root_prefix: str
    # "<bucket_name>/<root_prefix>", the s3fs path of the data root.
    data_root: str
    # "s3://<data_root>", the root of the s3 urls written to the db.
    s3_prefix: str
    # URL that serves the data root, the root of the https urls written to the db.
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
        # bucket_name may name a prefix inside the bucket: "bucket/prefix" or "s3://bucket/prefix/"
        self.bucket_name, self.root_prefix = self.split_bucket_path(bucket_name)
        self.data_root = f"{self.bucket_name}/{self.root_prefix}" if self.root_prefix else self.bucket_name
        self.s3_prefix = f"s3://{self.data_root}"
        self.https_prefix = https_prefix if https_prefix else PROD_URL
        if self.root_prefix and not self.https_prefix.rstrip("/").endswith(f"/{self.root_prefix}"):
            logger.warning(
                "Importing from s3://%s, but the https prefix %s does not end with %s. The https prefix should be "
                "the URL of the data root, so the https urls in the db may not resolve.",
                self.data_root,
                self.https_prefix,
                self.root_prefix,
            )
        self.session = session
        self.deposition_map: dict[int, models.Deposition] = {}

    @staticmethod
    def split_bucket_path(bucket_path: str) -> tuple[str, str]:
        """Splits "bucket", "bucket/prefix" or "s3://bucket/prefix/" into (bucket, prefix)."""
        bucket, _, prefix = bucket_path.removeprefix("s3://").strip("/").partition("/")
        return bucket, prefix.strip("/")

    def relative(self, path: str) -> str:
        """
        Returns the path relative to the data root. Accepts paths that are already relative to the data root, and
        "bucket/...", "bucket/<root_prefix>/..." or "s3://..." forms of those. A trailing slash is kept.
        """
        path = path.removeprefix("s3://")
        # The bare bucket form is for older metadata that wrote "bucket/10001/..." paths.
        for root in (self.data_root, self.bucket_name):
            if path == root:
                return ""
            if path.startswith(f"{root}/"):
                return path[len(root) + 1 :]
        return path

    def key(self, relative_path: str) -> str:
        """Returns the S3 key of a path relative to the data root."""
        return os.path.join(self.root_prefix, relative_path) if self.root_prefix else relative_path

    def from_key(self, key: str) -> str:
        """Returns the path relative to the data root of an S3 key (the inverse of key())."""
        if self.root_prefix and key.startswith(f"{self.root_prefix}/"):
            return key[len(self.root_prefix) + 1 :]
        return key

    def fs_path(self, relative_path: str) -> str:
        """Returns the s3fs path ("bucket/key") of a path relative to the data root."""
        return os.path.join(self.data_root, relative_path)

    def get_db_session(self) -> Session:
        return self.session

    def load_deposition_map(self) -> None:
        session = self.get_db_session()
        for item in session.scalars(sa.select(models.Deposition)).all():
            self.deposition_map[item.id] = item

    @lru_cache  # noqa
    def get_alignment_by_path(self, path: str, run_id: int) -> int | None:
        session = self.get_db_session()
        where_clauses = [
            models.Alignment.run_id == run_id,
            models.Alignment.s3_alignment_metadata == path,
        ]
        for item in session.scalars(sa.select(models.Alignment).where(sa.and_(*where_clauses))).all():
            return item.id

    @lru_cache  # noqa
    def get_tiltseries_by_path(self, path: str, run_id: int) -> int | None:
        session = self.get_db_session()
        # '_' is a wildcard character in sql LIKE queries, so we need to escape them (also in the root prefix)!
        tiltseries_dir = os.path.join(self.s3_prefix, os.path.dirname(self.relative(path)))
        path = os.path.join(tiltseries_dir.replace("_", "\\_"), "%")
        try:
            where_clauses = [
                models.Tiltseries.run_id == run_id,
                # tilt series ingested without MRC (--skip-mrc) only have the zarr in the tilt series directory
                sa.or_(models.Tiltseries.s3_mrc_file.like(path), models.Tiltseries.s3_omezarr_dir.like(path)),
            ]
            item = session.scalars(sa.select(models.Tiltseries).where(sa.and_(*where_clauses))).one()
            return item.id
        except NoResultFound:
            # We have a few runs that (erroneously) are missing tiltseries.
            # They need to be fixed, but in the meantime let's not fail ingestion
            # for the entire dataset based on that problem.
            return None

    def find_subdirs_with_files(self, prefix: str, target_filename: str) -> list[str]:
        paginator = self.s3_client.get_paginator("list_objects_v2")
        prefix = self.key(self.relative(prefix))
        logger.info("looking for prefix %s", prefix)
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter="/")
        result = []
        for page in pages:
            for obj in page.get("CommonPrefixes", []):
                try:
                    subdir = obj["Prefix"]
                    self.s3_client.head_object(Bucket=self.bucket_name, Key=f"{subdir}{target_filename}")
                    result.append(self.from_key(subdir))
                except Exception:
                    continue
        return result

    def recursive_glob_s3(self, prefix: str, glob_string: str) -> list[str]:
        # Returns path to a matched glob.
        s3 = self.s3fs
        prefix = self.relative(prefix).rstrip("/")
        path = os.path.join(self.data_root, prefix, glob_string)
        logger.info("Recursively looking for files in %s", path)
        return s3.glob(path)

    def recursive_glob_prefix(self, prefix: str, glob_string: str) -> list[str]:
        # Returns a prefix that contains a given glob'd path but not the path to the found item itself.
        s3 = self.s3fs
        prefix = self.relative(prefix).rstrip("/")
        path = os.path.join(self.data_root, prefix, glob_string)
        logger.info("Recursively looking for files in %s", path)
        return [os.path.dirname(self.relative(item)) for item in s3.glob(path)]

    def glob_s3(self, prefix: str, glob_string: str, is_file: bool = True):
        paginator = self.s3_client.get_paginator("list_objects_v2")
        prefix = self.key(self.relative(prefix))
        logger.info("looking for prefix %s%s", prefix, glob_string)
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter="/")
        page_key = "Contents" if is_file else "CommonPrefixes"
        obj_key = "Key" if is_file else "Prefix"
        for page in pages:
            for obj in page.get(page_key, {}):
                if not obj:
                    break
                if PurePath(obj[obj_key]).match(glob_string):
                    yield self.from_key(obj[obj_key])

    def load_key_json(self, key: str, is_file_required: bool = True) -> dict[str, Any] | None:
        """
        Loads file matching the key value as json. If file does not exist, will raise error if is_file_required is True
        else it will return None.
        """
        text = self.load_key_text(key, is_file_required)
        if text is None:
            return None
        return json.loads(text)

    def load_key_text(self, key: str, is_file_required: bool = True) -> str | None:
        """
        Loads file matching the key value as text. If file does not exist, will raise error if is_file_required is True
        else it will return None.
        """
        try:
            key = self.key(self.relative(key))
            text = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return text["Body"].read().decode("utf-8")
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
