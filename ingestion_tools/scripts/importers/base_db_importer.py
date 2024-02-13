import json
import os
from typing import Any, Optional

import boto3
import peewee

from botocore import UNSIGNED
from botocore.config import Config
from botocore.exceptions import ClientError

from common.db_models import BaseModel


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
            https_prefix: str = "https://files.cryoetdataportal.cziscience.com"
    ):
        self.s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED)) if anonymous else boto3.client("s3")
        self.bucket_name = bucket_name
        self.s3_prefix = "s3://{bucket_name}"
        self.https_prefix = https_prefix

    def find_subdirs_with_files(self, prefix: str, target_filename: str):
        paginator = self.s3_client.get_paginator("list_objects_v2")
        print(f"looking for prefix {prefix}")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, Delimiter="/")

        for page in pages:
            for obj in page["CommonPrefixes"]:
                subdir = obj["Prefix"]
                try:
                    metadata_key = f"{subdir}{target_filename}"
                    self.s3_client.head_object(Bucket=self.bucket_name, Key=metadata_key)
                except Exception:
                    continue
                yield subdir

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

    def join_path(*args) -> str:
        return os.path.join(*args)

    def get_metadata_file_path(self) -> str:
        pass

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
        pass

    def get_id_fields(self) -> set[str]:
        pass

    def get_db_model_class(self) -> type:
        pass

    def import_to_db(self) -> BaseModel:
        metadata = self.config.load_key_json(self.get_metadata_file_path())
        # TODO: print metadata if debug
        data_map = self.get_data_map(metadata)
        identifiers = {id_field: map_to_value(id_field, data_map, metadata) for id_field in self.get_id_fields()}

        klass = self.get_db_model_class()
        force_insert = False
        try:
            db_obj = klass.get(*[getattr(klass, k) == v for k, v in identifiers.items()])
        except peewee.DoesNotExist:
            db_obj = klass()
            force_insert = True

        for db_key, data_path in data_map.items():
            setattr(db_obj, db_key, map_to_value(db_key, data_map, metadata))

        db_obj.save(force_insert=force_insert)
        return db_obj
