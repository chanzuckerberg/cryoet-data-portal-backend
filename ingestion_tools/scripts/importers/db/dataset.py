from typing import Any, Iterable

from common import db_models
from importers.db.base_importer import (
    BaseDBImporter,
    DBImportConfig,
    StaleDeletionDBImporter,
    AuthorsStaleDeletionDBImporter,
)


class DatasetDBImporter(BaseDBImporter):
    def __init__(self, dir_prefix: str, config: DBImportConfig):
        self.config = config
        self.dir_prefix = dir_prefix
        self.parent = None
        self.metadata = config.load_key_json(self.get_metadata_file_path())

    def get_metadata_file_path(self) -> str:
        return self.join_path(self.dir_prefix, "dataset_metadata.json")

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {**self.get_direct_mapped_fields(), **self.get_computed_fields(metadata)}

    def get_id_fields(self) -> list[str]:
        return ["id"]

    def get_db_model_class(self) -> type:
        return db_models.Dataset

    @classmethod
    def get_direct_mapped_fields(cls) -> dict[str, Any]:
        return {
            "id": ["dataset_identifier"],
            "title": ["dataset_title"],
            "description": ["dataset_description"],
            "deposition_date": ["dates", "deposition_date"],
            "release_date": ["dates", "release_date"],
            "last_modified_date": ["dates", "last_modified_date"],
            "related_database_entries": ["cross_references", "related_database_entries"],
            "related_database_links": ["cross_references", "related_database_links"],
            "dataset_publications": ["cross_references", "dataset_publications"],
            "dataset_citations": ["cross_references", "dataset_citations"],
            "sample_type": ["sample_type"],
            "organism_name": ["organism", "name"],
            "organism_taxid": ["organism", "taxonomy_id"],
            "tissue_name": ["tissue", "name"],
            "tissue_id": ["tissue", "id"],
            "cell_name": ["cell_type", "name"],
            "cell_type_id": ["cell_type", "id"],
            "cell_strain_name": ["cell_strain", "name"],
            "cell_strain_id": ["cell_strain", "id"],
            "cell_component_name": ["cell_component", "name"],
            "cell_component_id": ["cell_component", "id"],
            "sample_preparation": ["sample_preparation"],
            "grid_preparation": ["grid_preparation"],
            "other_setup": ["other_setup"],
        }

    def get_computed_fields(self, metadata: dict[str, Any]) -> dict[str, Any]:
        https_prefix = self.config.https_prefix
        extra_data = {
            "s3_prefix": self.join_path(self.config.s3_prefix, self.dir_prefix),
            "https_prefix": self.join_path(https_prefix, self.dir_prefix),
            "key_photo_url": None,
            "key_photo_thumbnail_url": None,
        }
        key_photos = metadata.get("key_photos", {})
        if snapshot_path := key_photos.get("snapshot"):
            extra_data["key_photo_url"] = self.join_path(https_prefix, snapshot_path)
        if thumbnail_path := key_photos.get("thumbnail"):
            extra_data["key_photo_thumbnail_url"] = self.join_path(https_prefix, thumbnail_path)
        return extra_data

    @classmethod
    def get_items(cls, config: DBImportConfig, prefix: str) -> Iterable["DatasetDBImporter"]:
        return [
            cls(dataset_id, config) for dataset_id in config.find_subdirs_with_files(prefix, "dataset_metadata.json")
        ]


class DatasetAuthorDBImporter(StaleDeletionDBImporter):
    def __init__(self, dataset_id: int, parent: DatasetDBImporter, config: DBImportConfig):
        self.dataset_id = dataset_id
        self.parent = parent
        self.config = config
        self.metadata = parent.metadata.get("authors", [])

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
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

    def get_id_fields(self) -> list[str]:
        return ["dataset_id", "name"]

    def get_db_model_class(self) -> type:
        return db_models.DatasetAuthor

    def get_filters(self) -> dict[str, Any]:
        return {"dataset_id": self.dataset_id}

    @classmethod
    def get_item(cls, dataset_id: int, parent: DatasetDBImporter, config: DBImportConfig) -> "DatasetAuthorDBImporter":
        return cls(dataset_id, parent, config)


class DatasetFundingDBImporter(AuthorsStaleDeletionDBImporter):
    def __init__(self, dataset_id: int, parent: DatasetDBImporter, config: DBImportConfig):
        self.dataset_id = dataset_id
        self.parent = parent
        self.config = config
        self.metadata = parent.metadata.get("funding", [])

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "funding_agency_name": ["funding_agency_name"],
            "grant_id": ["grant_id"],
        }

    def get_id_fields(self) -> list[str]:
        return ["dataset_id", "funding_agency_name"]

    def get_db_model_class(self) -> type:
        return db_models.DatasetFunding

    def get_filters(self) -> dict[str, Any]:
        return {"dataset_id": self.dataset_id}

    @classmethod
    def get_item(cls, dataset_id: int, parent: DatasetDBImporter, config: DBImportConfig) -> "DatasetFundingDBImporter":
        return cls(dataset_id, parent, config)
