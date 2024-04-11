from typing import Any, Iterator

from common import db_models
from common.db_models import BaseModel
from importers.db.base_importer import (
    AuthorsStaleDeletionDBImporter,
    BaseDBImporter,
    DBImportConfig,
    StaleDeletionDBImporter,
    StaleParentDeletionDBImporter,
)
from importers.db.voxel_spacing import TomogramVoxelSpacingDBImporter


class AnnotationDBImporter(BaseDBImporter):
    def __init__(
        self,
        voxel_spacing_id: int,
        dir_prefix: str,
        metadata_filename: str,
        parent: TomogramVoxelSpacingDBImporter,
        config: DBImportConfig,
    ):
        self.voxel_spacing_id = voxel_spacing_id
        # TODO: update name
        self.dir_prefix = dir_prefix
        self.parent = parent
        self.config = config
        self.metadata_path = metadata_filename
        self.metadata = config.load_key_json(self.metadata_path)

    def get_data_map(self) -> dict[str, Any]:
        return {
            "tomogram_voxel_spacing_id": self.voxel_spacing_id,
            "s3_metadata_path": self.join_path(self.config.s3_prefix, self.metadata_path),
            "https_metadata_path": self.join_path(self.config.https_prefix, self.metadata_path),
            "deposition_date": ["dates", "deposition_date"],
            "release_date": ["dates", "release_date"],
            "last_modified_date": ["dates", "last_modified_date"],
            "annotation_publication": ["annotation_publications"],
            "annotation_method": ["annotation_method"],
            "ground_truth_status": ["ground_truth_status"],
            "object_name": ["annotation_object", "name"],
            "object_id": ["annotation_object", "id"],
            "object_description": ["annotation_object", "description"],
            "object_state": ["annotation_object", "state"],
            "object_count": ["object_count"],
            "confidence_precision": ["annotation_confidence", "precision"],
            "confidence_recall": ["annotation_confidence", "recall"],
            "ground_truth_used": ["annotation_confidence", "ground_truth_used"],
            "annotation_software": ["annotation_software"],
            "is_curator_recommended": ["is_curator_recommended"],
            "method_type": ["method_type"],
            "deposition_id": ["deposition_id"],
        }

    def import_to_db(self) -> BaseModel:
        annotation_obj = super().import_to_db()
        annotation_files = AnnotationFilesDBImporter.get_item(annotation_obj.id, self, self.config)
        annotation_files.import_to_db()
        return annotation_obj

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return ["s3_metadata_path"]

    @classmethod
    def get_db_model_class(cls) -> type[BaseModel]:
        return db_models.Annotation

    @classmethod
    def get_item(
        cls,
        voxel_spacing_id: int,
        voxel_spacing: TomogramVoxelSpacingDBImporter,
        config: DBImportConfig,
    ) -> Iterator["AnnotationDBImporter"]:
        annotation_dir_path = cls.join_path(voxel_spacing.dir_prefix, "Annotations/")
        return [
            cls(voxel_spacing_id, annotation_dir_path, annotation_metadata_path, voxel_spacing, config)
            for annotation_metadata_path in config.glob_s3(annotation_dir_path, "*.json")
        ]


class AnnotationFilesDBImporter(StaleDeletionDBImporter):
    def __init__(self, annotation_id: int, parent: AnnotationDBImporter, config: DBImportConfig):
        self.annotation_id = annotation_id
        self.parent = parent
        self.config = config
        self.metadata = parent.metadata.get("files", [])

    def get_data_map(self) -> dict[str, Any]:
        return {
            "annotation_id": self.annotation_id,
            "shape_type": ["shape"],
            "format": ["format"],
            "is_visualization_default": ["is_visualization_default"],
        }

    def update_data_map(self, data_map: dict[str, Any], metadata: dict[str, Any], index: int) -> dict[str, Any]:
        data_map["s3_path"] = self.join_path(self.config.s3_prefix, metadata["path"])
        data_map["https_path"] = self.join_path(self.config.https_prefix, metadata["path"])
        return data_map

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return ["annotation_id", "format", "shape_type"]

    @classmethod
    def get_db_model_class(cls) -> type[BaseModel]:
        return db_models.AnnotationFiles

    def get_filters(self) -> dict[str, Any]:
        return {"annotation_id": self.annotation_id}

    @classmethod
    def get_item(
        cls,
        annotation_id: int,
        parent: AnnotationDBImporter,
        config: DBImportConfig,
    ) -> "AnnotationFilesDBImporter":
        return cls(annotation_id, parent, config)


class AnnotationAuthorDBImporter(AuthorsStaleDeletionDBImporter):
    def __init__(self, annotation_id: int, parent: AnnotationDBImporter, config: DBImportConfig):
        self.annotation_id = annotation_id
        self.parent = parent
        self.config = config
        self.metadata = parent.metadata.get("authors", [])

    def get_data_map(self) -> dict[str, Any]:
        return {
            "annotation_id": self.annotation_id,
            "orcid": ["ORCID"],
            "name": ["name"],
            "primary_annotator_status": ["primary_author_status"],
            "corresponding_author_status": ["corresponding_author_status"],
            "email": ["email"],
            "affiliation_name": ["affiliation_name"],
            "affiliation_address": ["affiliation_address"],
            "affiliation_identifier": ["affiliation_identifier"],
            "author_list_order": ["author_list_order"],
        }

    def update_data_map(self, data_map: dict[str, Any], metadata: dict[str, Any], index: int) -> dict[str, Any]:
        if metadata.get("author_list_order"):
            return data_map
        if "primary_annotator_status" in metadata:
            data_map["primary_annotator_status"] = metadata["primary_annotator_status"]
        return {**data_map, **{"author_list_order": index + 1}}

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return ["annotation_id", "name"]

    @classmethod
    def get_db_model_class(cls) -> type[BaseModel]:
        return db_models.AnnotationAuthor

    def get_filters(self) -> dict[str, Any]:
        return {"annotation_id": self.annotation_id}

    @classmethod
    def get_item(
        cls,
        annotation_id: int,
        parent: AnnotationDBImporter,
        config: DBImportConfig,
    ) -> "AnnotationAuthorDBImporter":
        return cls(annotation_id, parent, config)


class StaleAnnotationDeletionDBImporter(StaleParentDeletionDBImporter):
    ref_klass = AnnotationDBImporter

    def get_filters(self) -> dict[str, Any]:
        return {"tomogram_voxel_spacing_id": self.parent_id}

    def children_tables_references(self) -> dict[str, None]:
        return {"authors": None, "files": None}
