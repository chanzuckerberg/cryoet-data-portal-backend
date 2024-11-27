import os
from typing import Any

from database import models
from db_import.common.finders import JsonDataFinder, MetadataFileFinder
from db_import.importers.base import IntegratedDBImporter, ItemDBImporter

# Alignment Fields
#  deposition_id: int
#  tiltseries_id: int
#  run_id: int
#  alignment_type: enum
#  volume_x_dimension: int
#  volume_y_dimension: int
#  volume_z_dimension: int
#  volume_x_offset: int
#  volume_y_offset: int
#  volume_z_offset: int
#  tilt_offset: int
#  id: int
#  x_rotation_offset: int
#  affine_transformation_matrix: list[list[int]]
#  alignment_method: enum
#  s3_alignment_metadata: str
#  https_alignment_metadata: str
#  is_portal_standard: bool


class AlignmentItem(ItemDBImporter):
    direct_mapped_fields = {
        "deposition_id": ["deposition_id"],
        "alignment_type": ["alignment_type"],
        "volume_x_dimension": ["volume_dimension", "x"],
        "volume_y_dimension": ["volume_dimension", "y"],
        "volume_z_dimension": ["volume_dimension", "z"],
        "volume_x_offset": ["volume_offset", "x"],
        "volume_y_offset": ["volume_offset", "y"],
        "volume_z_offset": ["volume_offset", "z"],
        "tilt_offset": ["tilt_offset"],
        "x_rotation_offset": ["x_rotation_offset"],
        "affine_transformation_matrix": ["affine_transformation_matrix"],
        "alignment_method": ["method_type"],
        "is_portal_standard": ["is_portal_standard"],
    }
    id_fields = ["run_id", "deposition_id"]
    model_class = models.Alignment

    def load_computed_fields(self):
        if self.model_args["alignment_method"] == "undefined":
            self.model_args["alignment_method"] = None
        self.model_args["s3_alignment_metadata"] = self.get_s3_url(self.input_data["file"])
        self.model_args["https_alignment_metadata"] = self.get_https_url(self.input_data["file"])
        if self.input_data.get("tiltseries_path"):
            self.model_args["tiltseries_id"] = self.config.get_tiltseries_by_path(self.input_data["tiltseries_path"])
        if not self.model_args["tiltseries_id"]:
            raise Exception("tiltseries id is required")
        self.model_args["run_id"] = self.input_data["run"].id


class AlignmentImporter(IntegratedDBImporter):
    finder = MetadataFileFinder
    row_importer = AlignmentItem
    clean_up_siblings = True

    def __init__(self, config, run: models.Run, **unused_parents):
        self.run = run
        self.config = config
        self.parents = {"run": run}

    def get_filters(self) -> dict[str, Any]:
        return {"run_id": self.run.id}

    def get_finder_args(self) -> dict[str, Any]:
        return {
            "path": os.path.join(self.run.s3_prefix, "Alignments/"),
            "file_glob": "*/alignment_metadata.json",
        }


class PerSectionAlignmentParametersItem(ItemDBImporter):
    id_fields = ["alignment_id", "z_index"]
    model_class = models.PerSectionAlignmentParameters
    direct_mapped_fields = {
        "z_index": ["z_index"],
        "tilt_angle": ["tilt_angle"],
        "volume_x_rotation": ["volume_x_rotation"],
        "in_plane_rotation": ["in_plane_rotation"],
        "x_offset": ["x_offset"],
        "y_offset": ["y_offset"],
    }

    def load_computed_fields(self):
        self.model_args["alignment_id"] = self.input_data["alignment"].id


class PerSectionAlignmentParametersImporter(IntegratedDBImporter):
    finder = JsonDataFinder
    row_importer = PerSectionAlignmentParametersItem
    clean_up_siblings = True

    def __init__(self, config, alignment: models.Alignment, **unused_parents):
        self.alignment = alignment
        self.config = config
        self.parents = {"alignment": alignment}

    def get_filters(self) -> dict[str, Any]:
        return {"alignment_id": self.alignment.id}

    def get_finder_args(self) -> dict[str, Any]:
        metadata_path = self.alignment.s3_alignment_metadata
        return {
            "path": self.convert_to_finder_path(metadata_path),
            "list_key": ["per_section_alignment_parameters"],
        }
