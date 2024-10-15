import json
import os
from typing import Any

from database import models
from db_import.common.finders import MetadataFileFinder
from db_import.common.normalize_fields import normalize_fiducial_alignment
from db_import.importers.base import IntegratedDBImporter, ItemDBImporter


class TomogramItem(ItemDBImporter):
    # TODO - add the alignment_id field once that data is added the first time.
    # id_fields = ["run_id", "tomogram_voxel_spacing_id", "deposition_id", "alignment_id", "processing", "reconstruction_method""]
    id_fields = ["run_id", "tomogram_voxel_spacing_id", "deposition_id", "processing", "reconstruction_method"]
    model_class = models.Tomogram
    direct_mapped_fields = {
        "name": ["run_name"],
        "size_x": ["size", "x"],
        "size_y": ["size", "y"],
        "size_z": ["size", "z"],
        "voxel_spacing": ["voxel_spacing"],
        "processing": ["processing"],
        "processing_software": ["processing_software"],
        "tomogram_version": ["tomogram_version"],
        "offset_x": ["offset", "x"],
        "offset_y": ["offset", "y"],
        "offset_z": ["offset", "z"],
        "deposition_id": ["deposition_id"],
        "deposition_date": ["dates", "deposition_date"],
        "release_date": ["dates", "release_date"],
        "last_modified_date": ["dates", "last_modified_date"],
    }

    def normalize_to_unknown_str(self, value: str) -> str:
        return value if value else "Unknown"

    def generate_neuroglancer_data(self, path) -> str:
        config = self.config.load_key_json(path, is_file_required=False)
        # TODO: Log warning
        return json.dumps(config, separators=(",", ":")) if config else "{}"

    def load_computed_fields(self):
        https_prefix = self.config.https_prefix
        s3_prefix = self.config.s3_prefix
        tomo_s3_path = os.path.dirname(self.input_data["file"])
        extra_data = {
            "ctf_corrected": bool(self.input_data.get("ctf_corrected")),
            "tomogram_voxel_spacing_id": self.input_data["tomogram_voxel_spacing"].id,
            "run_id": self.input_data["run"].id,
            "fiducial_alignment_status": normalize_fiducial_alignment(
                self.input_data.get("fiducial_alignment_status", False),
            ),
            "reconstruction_method": self.normalize_to_unknown_str(self.input_data.get("reconstruction_method")),
            "reconstruction_software": self.normalize_to_unknown_str(self.input_data.get("reconstruction_software")),
            "s3_omezarr_dir": os.path.join(s3_prefix, tomo_s3_path, self.input_data["omezarr_dir"]),
            "https_omezarr_dir": os.path.join(https_prefix, tomo_s3_path, self.input_data["omezarr_dir"]),
            "s3_mrc_file": os.path.join(s3_prefix, tomo_s3_path, self.input_data["mrc_files"][0]),
            "https_mrc_file": os.path.join(https_prefix, tomo_s3_path, self.input_data["mrc_files"][0]),
            # TODO: Add alignment_id once we have an alignment importer.
            "alignment_id": self.config.get_alignment_by_path(self.input_data["alignment_metadata_path"]),
            "key_photo_url": None,
            "key_photo_thumbnail_url": None,
            "is_portal_standard": self.input_data.get("is_standardized") or False,
            "is_visualization_default": False,
            "is_author_submitted": bool(
                self.input_data["deposition_id"] == self.input_data["run"].dataset.deposition_id,
            ),
        }
        if ng_config := self.input_data.get("neuroglancer_config_path"):
            extra_data["neuroglancer_config"] = self.generate_neuroglancer_data(ng_config)
        if key_photos := self.input_data.get("key_photo"):
            extra_data["key_photo_url"] = os.path.join(https_prefix, key_photos.get("snapshot"))
            extra_data["key_photo_thumbnail_url"] = os.path.join(https_prefix, key_photos.get("thumbnail"))

        for i in range(0, 3):
            scale = self.input_data["scales"][i]
            extra_data[f"scale{i}_dimensions"] = ",".join([str(scale[p]) for p in "xyz"])

        self.model_args.update(extra_data)


class TomogramImporter(IntegratedDBImporter):
    finder = MetadataFileFinder
    row_importer = TomogramItem
    clean_up_siblings = True  # TODO should be true

    def __init__(self, config, run: models.Run, voxel_spacing: models.TomogramVoxelSpacing, **unused_parents):
        self.run = run
        self.voxel_spacing = voxel_spacing
        self.config = config
        self.parents = {"run": run, "tomogram_voxel_spacing": voxel_spacing}

    def get_filters(self) -> dict[str, Any]:
        return {"tomogram_voxel_spacing_id": self.voxel_spacing.id}

    def get_finder_args(self) -> dict[str, Any]:
        return {
            "path": os.path.join(self.voxel_spacing.s3_prefix, "Tomograms/"),
            "file_glob": "*/tomogram_metadata.json",
        }


class TomogramAuthorItem(ItemDBImporter):
    # TODO - add the alignment_id field once that data is added the first time.
    # id_fields = ["run_id", "tomogram_voxel_spacing_id", "deposition_id", "alignment_id", "processing", "reconstruction_method""]
    id_fields = ["tomogram_id", "name"]
    model_class = models.TomogramAuthor
    direct_mapped_fields = {
        "orcid": ["ORCID"],
        "name": ["name"],
        "primary_author_status": ["primary_author_status"],
        "corresponding_author_status": ["corresponding_author_status"],
        "email": ["email"],
        "affiliation_name": ["affiliation_name"],
        "affiliation_address": ["affiliation_address"],
        "affiliation_identifier": ["affiliation_identifier"],
        "author_list_order": ["index"],
    }

    def load_computed_fields(self):
        self.model_args["tomogram_id"] = self.input_data["tomogram"].id


class TomogramAuthorImporter(IntegratedDBImporter):
    finder = MetadataFileFinder
    row_importer = TomogramAuthorItem
    clean_up_siblings = True  # TODO should be true

    def __init__(self, config, tomogram: models.Tomogram, **unused_parents):
        self.tomogram = tomogram
        self.config = config
        self.parents = {"tomogram": tomogram}

    def get_filters(self) -> dict[str, Any]:
        return {"tomogram_id": self.tomogram.id}

    def get_finder_args(self) -> dict[str, Any]:
        metadata_path = os.path.dirname(self.tomogram.s3_mrc_file)
        return {
            "path": metadata_path,
            "file_glob": "tomogram_metadata.json",
            "list_key": "authors",
        }
