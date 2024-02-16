from typing import Any, Iterator

from common import db_models
from common.db_models import BaseModel
from importers.db.base_importer import BaseDBImporter, DBImportConfig, AuthorsStaleDeletionDBImporter
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

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
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
        }

    def import_to_db(self) -> BaseModel:
        annotation_obj = super().import_to_db()
        for annotation_file in AnnotationFilesDBImporter.get_item(annotation_obj.id, self, self.config):
            annotation_file.import_to_db()
        return annotation_obj

    def get_id_fields(self) -> list[str]:
        return ["s3_metadata_path"]

    def get_db_model_class(self) -> type:
        return db_models.Annotation

    @classmethod
    def get_item(
        cls, voxel_spacing_id: int, voxel_spacing: TomogramVoxelSpacingDBImporter, config: DBImportConfig
    ) -> Iterator["AnnotationDBImporter"]:
        annotation_dir_path = cls.join_path(voxel_spacing.dir_prefix, "Annotations/")
        return [
            cls(voxel_spacing_id, annotation_dir_path, annotation_metadata_path, voxel_spacing, config)
            for annotation_metadata_path in config.glob_s3(annotation_dir_path, "*.json")
        ]


class AnnotationFilesDBImporter(BaseDBImporter):
    def __init__(
        self, annotation_id: int, parent: AnnotationDBImporter, config: DBImportConfig, metadata: dict[str, Any]
    ):
        self.annotation_id = annotation_id
        self.parent = parent
        self.config = config
        self.metadata = metadata

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "annotation_id": self.annotation_id,
            "shape_type": ["shape"],
            "format": ["format"],
            "s3_path": self.join_path(self.config.s3_prefix, self.metadata["path"]),
            "https_path": self.join_path(self.config.https_prefix, self.metadata["path"]),
            "is_visualization_default": ["is_visualization_default"],
        }

    def get_id_fields(self) -> list[str]:
        return ["annotation_id", "format", "shape_type"]

    def get_db_model_class(self) -> type:
        return db_models.AnnotationFiles

    @classmethod
    def get_item(
        cls, annotation_id: int, annotation: AnnotationDBImporter, config: DBImportConfig
    ) -> Iterator["AnnotationFilesDBImporter"]:
        return [
            cls(annotation_id, annotation, config, annotation_files_metadata)
            for annotation_files_metadata in annotation.metadata.get("files", [])
        ]


class AnnotationAuthorDBImporter(AuthorsStaleDeletionDBImporter):
    def __init__(self, annotation_id: int, parent: AnnotationDBImporter, config: DBImportConfig):
        self.annotation_id = annotation_id
        self.parent = parent
        self.config = config
        self.metadata = parent.metadata.get("authors", [])

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "annotation_id": self.annotation_id,
            "orcid": ["ORCID"],
            "name": ["name"],
            "primary_annotator_status": ["primary_annotator_status"],
            "corresponding_author_status": ["corresponding_author_status"],
            "email": ["email"],
            "affiliation_name": ["affiliation_name"],
            "affiliation_address": ["affiliation_address"],
            "affiliation_identifier": ["affiliation_identifier"],
            "author_list_order": ["author_list_order"],
        }

    def get_id_fields(self) -> list[str]:
        return ["annotation_id", "name"]

    def get_db_model_class(self) -> type:
        return db_models.AnnotationAuthor

    def get_filters(self) -> dict[str, Any]:
        return {"annotation_id": self.annotation_id}

    @classmethod
    def get_item(
        cls, dataset_id: int, parent: AnnotationDBImporter, config: DBImportConfig
    ) -> "AnnotationAuthorDBImporter":
        return cls(dataset_id, parent, config)
