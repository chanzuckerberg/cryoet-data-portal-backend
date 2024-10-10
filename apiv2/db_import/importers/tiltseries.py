from typing import Any

from database import models
from db_import.common.config import DBImportConfig
from db_import.importers.base_importer import BaseDBImporter, StaleParentDeletionDBImporter
from db_import.importers.deposition import get_deposition
from db_import.importers.run import RunDBImporter

from platformics.database.models.base import Base


class TiltSeriesDBImporter(BaseDBImporter):
    def __init__(self, run_id: int, dir_prefix: str, parent: RunDBImporter, config: DBImportConfig):
        self.run_id = run_id
        self.dir_prefix = dir_prefix
        self.parent = parent
        self.config = config
        self.metadata = config.load_key_json(self.get_metadata_file_path())

    def get_metadata_file_path(self) -> str:
        return self.join_path(self.dir_prefix, "tiltseries_metadata.json")

    def get_data_map(self) -> dict[str, Any]:
        return {**self.get_direct_mapped_fields(), **self.get_computed_fields()}

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return ["run_id"]

    @classmethod
    def get_db_model_class(cls) -> type[Base]:
        return models.Tiltseries

    @classmethod
    def get_direct_mapped_fields(cls) -> dict[str, Any]:
        return {
            "acceleration_voltage": ["acceleration_voltage"],
            "binning_from_frames": ["binning_from_frames"],
            "pixel_spacing": ["pixel_spacing"],
            "spherical_aberration_constant": ["spherical_aberration_constant"],
            "microscope_manufacturer": ["microscope", "manufacturer"],
            "microscope_model": ["microscope", "model"],
            "microscope_energy_filter": ["microscope_optical_setup", "energy_filter"],
            "microscope_phase_plate": ["microscope_optical_setup", "phase_plate"],
            "microscope_image_corrector": ["microscope_optical_setup", "image_corrector"],
            "microscope_additional_info": ["microscope", "additional_info"],
            "camera_manufacturer": ["camera", "manufacturer"],
            "camera_model": ["camera", "model"],
            "tilt_step": ["tilt_step"],
            "tilting_scheme": ["tilting_scheme"],
            "tilt_axis": ["tilt_axis"],
            "total_flux": ["total_flux"],
            "data_acquisition_software": ["data_acquisition_software"],
            "related_empiar_entry": ["related_empiar_entry"],
            "tilt_series_quality": ["tilt_series_quality"],
            "aligned_tiltseries_binning": ["aligned_tiltseries_binning"],
            "frames_count": ["frames_count"],
        }

    def get_first_match_file_name(self, file_extension_pattern: str):
        for key in self.config.glob_s3(self.dir_prefix, file_extension_pattern):
            return key

    def get_computed_fields(self) -> dict[str, Any]:
        https_prefix = self.config.https_prefix
        s3_prefix = self.config.s3_prefix
        tilt_max = float(self.metadata["tilt_range"]["max"])
        tilt_min = float(self.metadata["tilt_range"]["min"])
        extra_data = {
            "run_id": self.run_id,
            "tilt_min": round(tilt_min, 2),
            "tilt_max": round(tilt_max, 2),
            "tilt_range": round(abs(tilt_max - tilt_min), 2),
            "is_aligned": self.metadata.get("is_aligned") or False,
        }
        if mrc_path := self.metadata.get("mrc_files", [None])[0]:
            extra_data["s3_mrc_file"] = self.join_path(s3_prefix, self.dir_prefix, mrc_path)
            extra_data["https_mrc_file"] = self.join_path(https_prefix, self.dir_prefix, mrc_path)

        if omezarr_path := self.metadata.get("omezarr_dir"):
            extra_data["s3_omezarr_dir"] = self.join_path(s3_prefix, self.dir_prefix, omezarr_path)
            extra_data["https_omezarr_dir"] = self.join_path(https_prefix, self.dir_prefix, omezarr_path)

        if mdoc := self.get_first_match_file_name("*.mdoc"):
            extra_data["s3_collection_metadata"] = self.join_path(s3_prefix, mdoc)
            extra_data["https_collection_metadata"] = self.join_path(https_prefix, mdoc)

        if angle_list := self.get_first_match_file_name("*.rawtlt") or self.get_first_match_file_name("*.tlt"):
            extra_data["s3_angle_list"] = self.join_path(s3_prefix, angle_list)
            extra_data["https_angle_list"] = self.join_path(https_prefix, angle_list)

        if alignment_file_path := self.get_first_match_file_name("*.xf"):
            extra_data["s3_alignment_file"] = self.join_path(s3_prefix, alignment_file_path)
            extra_data["https_alignment_file"] = self.join_path(https_prefix, alignment_file_path)

        deposition = get_deposition(self.config, self.metadata.get("deposition_id"))
        extra_data["deposition_id"] = deposition.id

        return extra_data

    @classmethod
    def get_item(cls, run_id: int, run: RunDBImporter, config: DBImportConfig) -> "TiltSeriesDBImporter":
        ts_dir_path = cls.join_path(run.dir_prefix, "TiltSeries")
        ts_prefix = config.find_subdirs_with_files(ts_dir_path, "tiltseries_metadata.json")
        return cls(run_id, ts_prefix[0], run, config) if len(ts_prefix) > 0 else None


class StaleTiltSeriesDeletionDBImporter(StaleParentDeletionDBImporter):
    ref_klass = TiltSeriesDBImporter

    def get_filters(self) -> dict[str, Any]:
        return {"run_id": self.parent_id}

    def children_tables_references(self) -> dict[str, None]:
        return {}
