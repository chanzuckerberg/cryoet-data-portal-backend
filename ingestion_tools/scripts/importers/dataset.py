from typing import Any

from common import db_models
from common.metadata import DatasetMetadata
from importers.base_db_importer import BaseDBImporter, DBImportConfig
from importers.base_importer import BaseImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter


class DatasetImporter(BaseImporter):
    type_key = "dataset"

    def import_metadata(self, output_prefix: str) -> None:
        meta = DatasetMetadata(self.config.fs, self.config.dataset_template)
        extra_data = self.load_extra_metadata()
        meta.write_metadata(self.get_metadata_path(), extra_data)

    def load_extra_metadata(self) -> dict[str, dict[str, str]]:
        key_photo_importer = DatasetKeyPhotoImporter.find_dataset_key_photos(self.config, self)

        return {
            "key_photos": key_photo_importer.get_metadata(),
        }


class DatasetDBImporter(BaseDBImporter):
    type_key = "dataset"

    def __init__(self, dataset_id: str, config: DBImportConfig):
        self.config = config
        self.dir_prefix = dataset_id
        self.parent = None

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
        extra_data = {
            "s3_prefix": self.join_path(self.config.s3_prefix, self.dir_prefix),
            "https_prefix": self.join_path(self.config.https_prefix, self.dir_prefix),
            "key_photo_url": None,
            "key_photo_thumbnail_url": None,
        }
        key_photos = metadata.get("key_photos", {})
        https_prefix = self.config.https_prefix
        if snapshot_path := key_photos.get("snapshot"):
            extra_data["key_photo_url"] = self.join_path(https_prefix, snapshot_path)
        if thumbnail_path := key_photos.get("thumbnail"):
            extra_data["key_photo_thumbnail_url"] = self.join_path(https_prefix, thumbnail_path)
        return extra_data
