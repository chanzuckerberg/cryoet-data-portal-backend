import json
import logging
import os
from datetime import datetime
from pathlib import PurePath
from typing import TYPE_CHECKING, Any, Optional

import peewee
from botocore.exceptions import ClientError
from s3fs import S3FileSystem

from common.db_models import BaseModel

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

    def __init__(
        self,
        s3_client: S3Client,
        s3fs: S3FileSystem,
        bucket_name: str,
        https_prefix: str,
    ):
        self.s3_client = s3_client
        self.s3fs = s3fs
        self.bucket_name = bucket_name
        self.s3_prefix = f"s3://{bucket_name}"
        self.https_prefix = https_prefix if https_prefix else "https://files.cryoetdataportal.cziscience.com"

    def recursive_glob_s3(self, prefix: str, glob_string: str) -> list[str]:
        # Returns path to a matched glob.
        s3 = self.s3fs
        prefix = prefix.rstrip("/")
        path = os.path.join(self.bucket_name, prefix, glob_string)
        logger.info("Recursively looking for files in %s", path)
        def convert_to_key(str):
            return str[len(self.bucket_name) + 1 :]
        return [convert_to_key(item) for item in s3.glob(path)]

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
    def get_db_model_class(cls) -> type[BaseModel]:
        """Class to be used for generating the db object"""
        pass

    def import_to_db(self) -> BaseModel:
        """
        Gets the mapping, and queries to check if the table already has a record matching the id fields. If not, it will
        create a new object and insert it, else it will update the object with values from the metadata.
        """
        logger.debug(json.dumps(self.metadata, indent=2))
        data_map = self.get_data_map()
        identifiers = {id_field: map_to_value(id_field, data_map, self.metadata) for id_field in self.get_id_fields()}
        klass = self.get_db_model_class()
        force_insert = False
        try:
            db_obj = klass.get(*[getattr(klass, k) == v for k, v in identifiers.items()])
        except peewee.DoesNotExist:
            db_obj = klass()
            force_insert = True

        for db_key, _data_path in data_map.items():
            setattr(db_obj, db_key, map_to_value(db_key, data_map, self.metadata))

        db_obj.save(force_insert=force_insert)
        return db_obj

    def get_https_url(self, *input_path: tuple[str]) -> str:
        input_path = os.path.join(*input_path)
        if input_path.startswith(self.config.bucket_name):
            input_path = input_path[len(self.config.bucket_name) + 1 :]
        return os.path.join(self.config.https_prefix, input_path)

    def get_s3_url(self, *input_path: tuple[str]) -> str:
        input_path = os.path.join(*input_path)
        if input_path.startswith(self.config.bucket_name):
            input_path = input_path[len(self.config.bucket_name) + 1 :]
        return os.path.join(self.config.s3_prefix, input_path)


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
    def get_hash_value(cls, record: BaseModel) -> str:
        """
        Generates hash value for a record from values of its id fields separated by "-".
        """
        return "-".join([f"{getattr(record, attr)}" for attr in cls.get_id_fields()])

    def get_existing_objects(self) -> dict[str, BaseModel]:
        """
        Creates a map of existing items by querying using the filter criteria. The map is keyed on hash value of the
        record.
        """
        result = {}
        klass = self.get_db_model_class()
        query = klass.select().where(*[getattr(klass, k) == v for k, v in self.get_filters().items()])
        for record in query:
            result[self.get_hash_value(record)] = record
        return result

    def update_data_map(self, data_map: dict[str, Any], metadata: dict[str, Any], index: int) -> dict[str, Any]:
        """
        Method to be overridden in cases where custom data mapping is necessary based on index value of the record in
        the list.
        """
        return data_map

    def import_to_db(self) -> None:
        """
        Gets all the existing objects as a map for the current filter criteria. It creates/updates the records iterating
        over the metadata list, and popping any existing value from the map. After the iteration, the map only contains
        data that are no longer valid. Those stale records are deleted from the table.
        """
        klass = self.get_db_model_class()
        data_map = self.get_data_map()
        existing_objs = self.get_existing_objects()
        metadata_list = self.metadata if isinstance(self.metadata, list) else [self.metadata]

        for index, entry in enumerate(metadata_list):
            entry_data_map = self.update_data_map(data_map, entry, index)
            hash_values = [str(map_to_value(id_field, entry_data_map, entry)) for id_field in self.get_id_fields()]
            force_insert = False
            db_obj = existing_objs.pop("-".join(hash_values), None)
            if not db_obj:
                db_obj = klass()
                force_insert = True

            for db_key, _data_path in entry_data_map.items():
                setattr(db_obj, db_key, map_to_value(db_key, entry_data_map, entry))
            db_obj.save(force_insert=force_insert)

        for key, stale_obj in existing_objs.items():
            logger.info("Deleting record of %s with id=%d and key=%s", klass, stale_obj.id, key)
            stale_obj.delete_instance()


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
    existing_objects: dict[str, BaseModel]
    config: DBImportConfig
    parent_id: int

    def __init__(self, parent_id: int, config: DBImportConfig):
        self.parent_id = parent_id
        self.config = config
        self.existing_objects = self.get_existing_objects()

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return cls.ref_klass.get_id_fields()

    @classmethod
    def get_db_model_class(cls) -> type:
        return cls.ref_klass.get_db_model_class()

    @classmethod
    def children_tables_references(cls) -> dict[str, "type[StaleParentDeletionDBImporter]"]:
        """
        Specifies the deletion helper for the tables that could reference have a foreign key relationship with this
        record.
        The deletion helper could either be None if the table is not referenced anywhere or an object of type
        StaleParentDeletionDBImporter if it is also in turn referenced in other places.
        """
        pass

    def mark_as_active(self, record: BaseModel):
        """Mark a record as active by removing it from existing objects when encountered."""
        logger.info(
            "marking as active %s with identifiers %s",
            self.ref_klass.get_db_model_class(),
            self.get_hash_value(record),
        )
        self.existing_objects.pop(self.get_hash_value(record), None)

    def remove_stale_objects(self):
        """
        Deletes all stale objects by deleting the records that have the foreign key references first, and then deletes
        the stale object.
        """
        for key, stale_obj in self.existing_objects.items():
            for child_rel, deletion_helper in self.children_tables_references().items():
                for entry in getattr(stale_obj, child_rel):
                    if deletion_helper is None:
                        logger.info(
                            "Deleting record of %s with id=%d data=%s to delete parent: %s",
                            type(entry),
                            entry.id,
                            entry.__data__,
                            type(stale_obj),
                        )
                        entry.delete_instance()
                    else:
                        # Using stale_obj.id as all the use cases currently are satisfied by this.
                        klass = deletion_helper(stale_obj.id, self.config)
                        klass.remove_stale_objects()
            logger.info(
                "Deleting record of %s with id=%d and key=%s",
                self.ref_klass.get_db_model_class(),
                stale_obj.id,
                key,
            )
            stale_obj.delete_instance()
