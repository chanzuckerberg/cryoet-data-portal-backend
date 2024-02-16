import json
import os
from pathlib import PurePath
from typing import Any, Optional, Iterator

import boto3
import peewee

from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError

from common.db_models import BaseModel
import datetime


class DBImportConfig:
    # TODO: define better type
    s3_client: Any
    bucket_name: str
    s3_prefix: str
    https_prefix: str

    def __init__(
        self,
        anonymous: bool,
        bucket_name: str,
        https_prefix: str,
    ):
        self.s3_client = (
            boto3.client("s3", config=Config(signature_version=UNSIGNED)) if anonymous else boto3.client("s3")
        )
        self.bucket_name = bucket_name
        self.s3_prefix = f"s3://{bucket_name}"
        self.https_prefix = https_prefix if https_prefix else "https://files.cryoetdataportal.cziscience.com"

    def find_subdirs_with_files(self, prefix: str, target_filename: str) -> Iterator[str]:
        paginator = self.s3_client.get_paginator("list_objects_v2")
        print(f"looking for prefix {prefix}")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter="/")
        result = []
        for page in pages:
            for obj in page["CommonPrefixes"]:
                subdir = obj["Prefix"]
                try:
                    self.s3_client.head_object(Bucket=self.bucket_name, Key=f"{subdir}{target_filename}")
                    result.append(subdir)
                except Exception:
                    continue
        return result

    def glob_s3(self, prefix: str, glob_string: str, is_file: bool = True):
        paginator = self.s3_client.get_paginator("list_objects_v2")
        print(f"looking for prefix {prefix}{glob_string}")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter="/")
        page_key = "Contents" if is_file else "CommonPrefixes"
        obj_key = "Key" if is_file else "Prefix"
        for page in pages:
            for obj in page.get(page_key, {}):
                if not obj:
                    break
                if PurePath(obj[obj_key]).match(glob_string):
                    yield obj[obj_key]

    def load_key_json(self, key: str, is_file_required=True):
        try:
            text = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            data = json.loads(text["Body"].read())
            return data
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "NoSuchKey" and not is_file_required:
                print(f"NoSuchKey on bucket_name={self.bucket_name} key={key}")
                return None
            else:
                raise


def map_to_value(db_key: str, mapping: dict[str, Any], data: dict[str, Any]) -> Any:
    data_path = mapping.get(db_key)
    if not isinstance(data_path, list):
        return data_path

    value = None
    for pathpart in data_path:
        value = data.get(pathpart) if not value else value.get(pathpart)
        if not value:
            break
    if value and "date" in db_key:
        value = datetime.datetime.strptime(value, "%Y-%m-%d")  # type: ignore
    return value


class BaseDBImporter:
    prefix: str
    dir_prefix: str
    config: DBImportConfig
    parent: "Optional[BaseDBImporter]"
    metadata: dict[str, Any] | list[dict[str, Any]]

    @classmethod
    def join_path(cls, *args) -> str:
        return os.path.join(*args)

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
        pass

    def get_id_fields(self) -> set[str]:
        pass

    def get_db_model_class(self) -> type:
        pass

    def import_to_db(self) -> BaseModel:
        # TODO: print metadata if debug
        data_map = self.get_data_map(self.metadata)
        identifiers = {id_field: map_to_value(id_field, data_map, self.metadata) for id_field in self.get_id_fields()}
        klass = self.get_db_model_class()
        force_insert = False
        try:
            db_obj = klass.get(*[getattr(klass, k) == v for k, v in identifiers.items()])
        except peewee.DoesNotExist:
            db_obj = klass()
            force_insert = True

        for db_key, data_path in data_map.items():
            setattr(db_obj, db_key, map_to_value(db_key, data_map, self.metadata))

        db_obj.save(force_insert=force_insert)
        return db_obj


class StaleDeletionDBImporter(BaseDBImporter):
    def get_filters(self) -> dict[str, str]:
        pass

    def get_existing_objects(self) -> dict[str, BaseModel]:
        result = {}
        klass = self.get_db_model_class()
        query = klass.select().where(*[getattr(klass, k) == v for k, v in self.get_filters().items()])
        for record in query:
            key = "-".join([f"{getattr(record, attr)}" for attr in self.get_id_fields()])
            result[key] = record
        return result

    def update_data_map(self, data_map: dict[str, Any], metadata: dict[str, Any], index: int) -> dict[str, Any]:
        return data_map

    def import_to_db(self) -> None:
        klass = self.get_db_model_class()
        data_map = self.get_data_map(self.metadata)
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

            for db_key, data_path in entry_data_map.items():
                setattr(db_obj, db_key, map_to_value(db_key, entry_data_map, entry))
            db_obj.save(force_insert=force_insert)

        for stale_obj in existing_objs.values():
            # TODO: Log deletion
            stale_obj.delete_instance()


class AuthorsStaleDeletionDBImporter(StaleDeletionDBImporter):
    def update_data_map(self, data_map: dict[str, Any], metadata: dict[str, Any], index: int) -> dict[str, Any]:
        if metadata.get("author_list_order"):
            return data_map
        return {**data_map, **{"author_list_order": index + 1}}
