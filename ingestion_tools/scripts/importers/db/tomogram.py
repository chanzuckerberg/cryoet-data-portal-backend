import json
from typing import Any, Iterator

from common import db_models
from common.db_models import BaseModel
from common.normalize_fields import normalize_fiducial_alignment, normalize_to_none_str
from importers.db.base_importer import (
    AuthorsStaleDeletionDBImporter,
    BaseDBImporter,
    DBImportConfig,
    StaleParentDeletionDBImporter,
)
from importers.db.voxel_spacing import TomogramVoxelSpacingDBImporter


class TomogramDBImporter(BaseDBImporter):
    def __init__(
        self,
        voxel_spacing_id: int,
        dir_prefix: str,
        parent: TomogramVoxelSpacingDBImporter,
        config: DBImportConfig,
    ):
        self.voxel_spacing_id = voxel_spacing_id
        self.dir_prefix = dir_prefix
        self.parent = parent
        self.config = config
        self.metadata = config.load_key_json(self.get_metadata_file_path())

    def get_metadata_file_path(self) -> str:
        return self.join_path(self.dir_prefix, "tomogram_metadata.json")

    def get_data_map(self) -> dict[str, Any]:
        return {**self.get_direct_mapped_fields(), **self.get_computed_fields()}

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return ["name", "tomogram_voxel_spacing_id"]

    @classmethod
    def get_db_model_class(cls) -> type[BaseModel]:
        return db_models.Tomogram

    @classmethod
    def get_direct_mapped_fields(cls) -> dict[str, Any]:
        return {
            "name": ["run_name"],
            "size_x": ["size", "x"],
            "size_y": ["size", "y"],
            "size_z": ["size", "z"],
            "voxel_spacing": ["voxel_spacing"],
            "processing": ["processing"],
            "processing_software": ["processing_software"],
            "tomogram_version": ["tomogram_version"],
            "ctf_corrected": ["ctf_corrected"],
            "offset_x": ["offset", "x"],
            "offset_y": ["offset", "y"],
            "offset_z": ["offset", "z"],
            "affine_transformation_matrix": ["affine_transformation_matrix"],
        }

    def get_tomogram_type(self) -> str:
        if "CanonicalTomogram" in self.dir_prefix:
            return "CANONICAL"
        return "UNKOWN"

    def generate_neuroglancer_data(self) -> str:
        path = self.join_path(self.dir_prefix, "neuroglancer_config.json")
        config = self.config.load_key_json(path, is_file_required=False)
        # TODO: Log warning
        return json.dumps(config, separators=(",", ":")) if config else "{}"

    def get_computed_fields(self) -> dict[str, Any]:
        https_prefix = self.config.https_prefix
        s3_prefix = self.config.s3_prefix
        extra_data = {
            "tomogram_voxel_spacing_id": self.voxel_spacing_id,
            "fiducial_alignment_status": normalize_fiducial_alignment(self.metadata.get("fiducial_alignment_status")),
            "reconstruction_method": normalize_to_none_str(self.metadata.get("reconstruction_method")),
            "reconstruction_software": normalize_to_none_str(self.metadata.get("reconstruction_software")),
            "is_canonical": True,  # TODO: mark this for deprecation
            "s3_omezarr_dir": self.join_path(s3_prefix, self.dir_prefix, self.metadata["omezarr_dir"]),
            "https_omezarr_dir": self.join_path(https_prefix, self.dir_prefix, self.metadata["omezarr_dir"]),
            "s3_mrc_scale0": self.join_path(s3_prefix, self.dir_prefix, self.metadata["mrc_files"][0]),
            "https_mrc_scale0": self.join_path(https_prefix, self.dir_prefix, self.metadata["mrc_files"][0]),
            "key_photo_url": None,
            "key_photo_thumbnail_url": None,
            "neuroglancer_config": self.generate_neuroglancer_data(),
            "type": self.get_tomogram_type(),
        }
        if key_photos := self.metadata.get("key_photo"):
            extra_data["key_photo_url"] = self.join_path(https_prefix, key_photos.get("snapshot"))
            extra_data["key_photo_thumbnail_url"] = self.join_path(https_prefix, key_photos.get("thumbnail"))

        for i in range(0, 3):
            scale = self.metadata["scales"][i]
            extra_data[f"scale{i}_dimensions"] = ",".join([str(scale[p]) for p in "xyz"])

        return extra_data

    @classmethod
    def get_item(
        cls,
        voxel_spacing_id: int,
        voxel_spacing: TomogramVoxelSpacingDBImporter,
        config: DBImportConfig,
    ) -> Iterator["TomogramDBImporter"]:
        tomogram_dir_path = cls.join_path(voxel_spacing.dir_prefix, "CanonicalTomogram")
        return [
            cls(voxel_spacing_id, tomogram_prefix, voxel_spacing, config)
            for tomogram_prefix in config.find_subdirs_with_files(tomogram_dir_path, "tomogram_metadata.json")
        ]


class TomogramAuthorDBImporter(AuthorsStaleDeletionDBImporter):
    def __init__(self, tomogram_id: int, parent: TomogramDBImporter, config: DBImportConfig):
        self.tomogram_id = tomogram_id
        self.parent = parent
        self.config = config
        self.metadata = parent.metadata.get("authors", [])

    def get_data_map(self) -> dict[str, Any]:
        return {
            "tomogram_id": self.tomogram_id,
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
        return ["tomogram_id", "name"]

    @classmethod
    def get_db_model_class(cls) -> type[BaseModel]:
        return db_models.TomogramAuthor

    def get_filters(self) -> dict[str, Any]:
        return {"tomogram_id": self.tomogram_id}

    @classmethod
    def get_item(
        cls,
        dataset_id: int,
        parent: TomogramDBImporter,
        config: DBImportConfig,
    ) -> "TomogramAuthorDBImporter":
        return cls(dataset_id, parent, config)


class StaleTomogramDeletionDBImporter(StaleParentDeletionDBImporter):
    ref_klass = TomogramDBImporter

    def get_filters(self) -> dict[str, Any]:
        return {"tomogram_voxel_spacing_id": self.parent_id}

    def children_tables_references(self) -> dict[str, None]:
        return {"authors": None}
