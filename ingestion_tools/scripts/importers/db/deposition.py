from datetime import datetime, timezone
from typing import Any, Iterable

from common import db_models
from common.db_models import BaseModel
from importers.db.base_importer import AuthorsStaleDeletionDBImporter, BaseDBImporter, DBImportConfig


def to_datetime(ts: int | None) -> datetime:
    return datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None


class DepositionDBImporter(BaseDBImporter):
    def __init__(self, dir_prefix: str, config: DBImportConfig):
        self.config = config
        self.dir_prefix = dir_prefix
        self.parent = None
        self.metadata = config.load_key_json(self.get_metadata_file_path())

    def get_metadata_file_path(self) -> str:
        return self.join_path(self.dir_prefix, "deposition_metadata.json")

    def get_data_map(self) -> dict[str, Any]:
        return {**self.get_direct_mapped_fields(), **self.get_computed_fields()}

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return ["id"]

    @classmethod
    def get_db_model_class(cls) -> type[BaseModel]:
        return db_models.Deposition

    @classmethod
    def get_direct_mapped_fields(cls) -> dict[str, Any]:
        return {
            "id": ["deposition_identifier"],
            "title": ["deposition_title"],
            "description": ["deposition_description"],
            "deposition_date": ["dates", "deposition_date"],
            "release_date": ["dates", "release_date"],
            "last_modified_date": ["dates", "last_modified_date"],
            "related_database_entries": ["cross_references", "related_database_entries"],
            "deposition_publications": ["cross_references", "publications"],
        }

    def get_computed_fields(self) -> dict[str, Any]:
        extra_data = {
            "s3_prefix": self.get_s3_url(self.dir_prefix),
            "https_prefix": self.get_https_url(self.dir_prefix),
            "key_photo_url": None,
            "key_photo_thumbnail_url": None,
        }
        deposition_type = self.metadata.get("deposition_types", [])
        deposition_type.sort()
        extra_data["deposition_types"] = ",".join(deposition_type)
        key_photos = self.metadata.get("key_photos", {})
        if snapshot_path := key_photos.get("snapshot"):
            extra_data["key_photo_url"] = self.get_https_url(snapshot_path)
        if thumbnail_path := key_photos.get("thumbnail"):
            extra_data["key_photo_thumbnail_url"] = self.get_https_url(thumbnail_path)
        return extra_data

    @classmethod
    def get_items(cls, config: DBImportConfig, deposition_id: int | str) -> Iterable["DepositionDBImporter"]:
        return [
            cls(deposition_id, config)
            for deposition_id in config.find_subdirs_with_files(
                f"depositions_metadata/{deposition_id}",
                "deposition_metadata.json",
            )
        ]


class DepositionAuthorDBImporter(AuthorsStaleDeletionDBImporter):
    def __init__(self, deposition_id: int, parent: DepositionDBImporter, config: DBImportConfig):
        self.deposition_id = deposition_id
        self.parent = parent
        self.config = config
        self.metadata = parent.metadata.get("authors", [])

    def get_data_map(self) -> dict[str, Any]:
        return {
            "deposition_id": self.deposition_id,
            "orcid": ["ORCID"],
            "name": ["name"],
            "primary_author_status": ["primary_author_status"],
            "corresponding_author_status": ["corresponding_author_status"],
            "email": ["email"],
            "affiliation_name": ["affiliation_name"],
            "affiliation_address": ["affiliation_address"],
            "affiliation_identifier": ["affiliation_identifier"],
            "author_list_order": ["author_list_order"],
        }

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return ["deposition_id", "name"]

    @classmethod
    def get_db_model_class(cls) -> type[BaseModel]:
        return db_models.DepositionAuthor

    def get_filters(self) -> dict[str, Any]:
        return {"deposition_id": self.deposition_id}

    @classmethod
    def get_item(
        cls,
        deposition_id: int,
        parent: DepositionDBImporter,
        config: DBImportConfig,
    ) -> "DepositionAuthorDBImporter":
        return cls(deposition_id, parent, config)


# TODO: Make this a container that caches depositions so we aren't hitting the database multiple times for the same id
def get_deposition(config: DBImportConfig, deposition_id: str | int) -> db_models.Deposition:
    if not deposition_id:
        raise ValueError(f"invalid deposition_id provided {deposition_id}")

    deposition_id = int(deposition_id)
    deposition = db_models.Deposition.get_or_none(deposition_id)
    if deposition:
        return deposition

    depositions = []
    for deposition_importer in DepositionDBImporter.get_items(config, deposition_id):
        deposition_obj = deposition_importer.import_to_db()
        depositions.append(deposition_obj)
        deposition_authors = DepositionAuthorDBImporter.get_item(deposition_obj, deposition_importer, config)
        deposition_authors.import_to_db()

    if not depositions:
        raise ValueError(f"Deposition {deposition_id} not found")
    return depositions[0]
