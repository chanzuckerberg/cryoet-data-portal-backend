import json
import logging
import os
from datetime import datetime
from pathlib import PurePath
from typing import TYPE_CHECKING, Any, Optional

import sqlalchemy as sa
from botocore.exceptions import ClientError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from platformics.database.models.base import Base

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
else:
    S3Client = object

logger = logging.getLogger("db_import")


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


class BaseDBImporter:
    """Supports insert of new record, and update of existing record."""

    prefix: str
    dir_prefix: str
    config: DBImportConfig
    parent: "Optional[BaseDBImporter]"
    metadata: dict[str, Any] | list[dict[str, Any]]

    @classmethod
    def join_path(cls, *args) -> str:
        return os.path.join(*args)

    def get_data_map(self) -> dict[str, Any]:
        """Get mapping of json path to traverse in metadata or precomputed values for db fields"""
        pass

    @classmethod
    def get_id_fields(cls) -> list[str]:
        """Non id field(s) that can uniquely identify the record in the table to prevent duplication"""
        pass

    @classmethod
    def get_db_model_class(cls) -> type[Base]:
        """Class to be used for generating the db object"""
        pass

    def import_to_db(self) -> Base:
        """
        Gets the mapping, and queries to check if the table already has a record matching the id fields. If not, it will
        create a new object and insert it, else it will update the object with values from the metadata.
        """
        logger.debug(json.dumps(self.metadata, indent=2))
        data_map = self.get_data_map()
        identifiers = {id_field: map_to_value(id_field, data_map, self.metadata) for id_field in self.get_id_fields()}
        klass = self.get_db_model_class()
        session = self.config.get_db_session()
        try:
            query = sa.select(klass).where(sa.and_(*[getattr(klass, k) == v for k, v in identifiers.items()]))
            db_obj = session.scalars(query).one()
        except NoResultFound:
            db_obj = klass()

        for db_key, _data_path in data_map.items():
            setattr(db_obj, db_key, map_to_value(db_key, data_map, self.metadata))

        session.add(db_obj)
        session.flush()
        return db_obj


class StaleDeletionDBImporter(BaseDBImporter):
    """
    Supports insert of new record, update of existing record, and delete of stale records. This class iterates over a
    list of individual records. This is a good fit for tables that aren't referenced as foreign keys.
    """

    def get_filters(self) -> dict[str, str]:
        """
        Provides filter criteria for fetching all the sibling records.
        Ex: filter by dataset_id=XYZ on dataset_authors to fetch all authors of dataset XYZ.
        """
        pass

    @classmethod
    def get_hash_value(cls, record: Base) -> str:
        """
        Generates hash value for a record from values of its id fields separated by "-".
        """
        return "-".join([f"{getattr(record, attr)}" for attr in cls.get_id_fields()])

    def get_existing_objects(self) -> tuple[list[Base], dict[str, Base]]:
        """
        Creates a map of existing items by querying using the filter criteria. The map is keyed on hash value of the
        record.
        """
        hashed_records = {}
        klass = self.get_db_model_class()
        session = self.config.get_db_session()
        query = session.scalars(
            sa.select(klass).where(sa.and_(*[getattr(klass, k) == v for k, v in self.get_filters().items()])),
        ).all()
        all_records = []
        for record in query:
            all_records.append(record)
            hashed_records[self.get_hash_value(record)] = record
        return all_records, hashed_records

    def update_data_map(self, data_map: dict[str, Any], metadata: dict[str, Any], index: int) -> dict[str, Any]:
        """
        Method to be overridden in cases where custom data mapping is necessary based on index value of the record in
        the list.
        """
        return data_map

    def import_to_db(self) -> Base:
        """
        Gets all the existing objects as a map for the current filter criteria. It creates/updates the records iterating
        over the metadata list, and popping any existing value from the map. After the iteration, the map only contains
        data that are no longer valid. Those stale records are deleted from the table.
        """
        klass = self.get_db_model_class()
        data_map = self.get_data_map()
        records_to_delete, hashed_records = self.get_existing_objects()
        metadata_list = self.metadata if isinstance(self.metadata, list) else [self.metadata]
        session = self.config.get_db_session()

        db_obj = None
        for index, entry in enumerate(metadata_list):
            entry_data_map = self.update_data_map(data_map, entry, index)
            hash_values = [str(map_to_value(id_field, entry_data_map, entry)) for id_field in self.get_id_fields()]
            print(f"Lookup key {"-".join(hash_values)}")
            db_obj = hashed_records.get("-".join(hash_values))
            print(f"db obj is {db_obj}")
            if not db_obj:
                db_obj = klass()
            if db_obj in records_to_delete:
                records_to_delete.remove(db_obj)

            for db_key, _data_path in entry_data_map.items():
                setattr(db_obj, db_key, map_to_value(db_key, entry_data_map, entry))
            session.add(db_obj)

        for stale_obj in records_to_delete:
            logger.info("Deleting record of %s with id=%d and key=%s", klass, stale_obj.id, self.get_hash_value(stale_obj))
            session.delete(stale_obj)
        session.flush()
        return db_obj


class AuthorsStaleDeletionDBImporter(StaleDeletionDBImporter):
    """
    Supports insert of new authors, update of existing authors, and delete of stale authors. This class iterates over a
    list of individual authors.
    """

    def update_data_map(self, data_map: dict[str, Any], metadata: dict[str, Any], index: int) -> dict[str, Any]:
        """Adds author list order based on the index position to the author data"""
        if metadata.get("author_list_order"):
            return data_map
        return {**data_map, **{"author_list_order": index + 1}}


class StaleParentDeletionDBImporter(StaleDeletionDBImporter):
    """
    Helps in deletion of stale records that are referenced as foreign key in other tables.
    """

    ref_klass: type[BaseDBImporter]
    existing_objects: dict[str, Base]
    config: DBImportConfig
    parent_id: int

    def __init__(self, parent_id: int, config: DBImportConfig):
        self.parent_id = parent_id
        self.config = config
        self.existing_objects = self.get_existing_objects()
        self.records_to_delete, self.hashed_records = self.get_existing_objects()

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return cls.ref_klass.get_id_fields()

    @classmethod
    def get_db_model_class(cls) -> type:
        return cls.ref_klass.get_db_model_class()

    def mark_as_active(self, record: Base):
        """Mark a record as active by removing it from existing objects when encountered."""
        logger.info(
            "marking as active %s with identifiers %s",
            self.ref_klass.get_db_model_class(),
            self.get_hash_value(record),
        )
        matched_record = self.hashed_records.get(self.get_hash_value(record))
        if matched_record and matched_record in self.records_to_delete:
            self.records_to_delete.remove(matched_record)

    def remove_stale_objects(self):
        """
        Deletes all stale objects by deleting the records that have the foreign key references first, and then deletes
        the stale object.
        """
        session = self.config.get_db_session()
        for stale_obj in self.records_to_delete:
            logger.info(
                "Deleting record of %s with id=%d and key=%s",
                self.ref_klass.get_db_model_class(),
                stale_obj.id,
                self.get_hash_value(stale_obj),
            )
            session.delete(stale_obj)
        session.flush()
