from typing import Any

from common import db_models
from importers.db.base_importer import BaseDBImporter, DBImportConfig
from importers.db.run import RunDBImporter


class TiltSeriesDBImporter(BaseDBImporter):
    def __init__(self, run_id: int, dir_prefix: str, parent: RunDBImporter, config: DBImportConfig):
        self.run_id = run_id
        self.dir_prefix = dir_prefix
        self.parent = parent
        self.config = config
        self.metadata = config.load_key_json(self.get_metadata_file_path())

    def get_metadata_file_path(self) -> str:
        return self.join_path(self.dir_prefix, "tiltseries_metadata.json")

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {**self.get_direct_mapped_fields(), **self.get_computed_fields(metadata)}

    def get_id_fields(self) -> list[str]:
        return ["run_id"]

    def get_db_model_class(self) -> type:
        return db_models.TiltSeries

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
            "microscope_additional_info": ["microscope_additional_info"],
            "camera_manufacturer": ["camera", "manufacturer"],
            "camera_model": ["camera", "model"],
            "tilt_min": ["tilt_range", "min"],
            "tilt_max": ["tilt_range", "max"],
            "tilt_step": ["tilt_step"],
            "tilting_scheme": ["tilting_scheme"],
            "tilt_axis": ["tilt_axis"],
            "total_flux": ["total_flux"],
            "data_acquisition_software": ["data_acquisition_software"],
            "related_empiar_entry": ["empiar_entry"],
            "tilt_series_quality": ["tilt_series_quality"],
            "is_aligned": ["is_aligned"],
            "aligned_tiltseries_binning": ["aligned_tiltseries_binning"],
            "frames_count": ["frames_count"],
        }

    def get_first_match_file_name(self, file_extension_pattern: str):
        for key in self.config.glob_s3(self.dir_prefix, file_extension_pattern):
            return key

    def get_computed_fields(self, metadata: dict[str, Any]) -> dict[str, Any]:
        https_prefix = self.config.https_prefix
        s3_prefix = self.config.s3_prefix
        extra_data = {
            "run_id": self.run_id,
            "tilt_range": abs(float(metadata["tilt_range"]["max"]) - float(metadata["tilt_range"]["min"])),
        }
        if mrc_path := metadata.get("mrc_files", [None])[0]:
            extra_data["s3_mrc_bin1"] = self.join_path(s3_prefix, self.dir_prefix, mrc_path)
            extra_data["https_mrc_bin1"] = self.join_path(https_prefix, self.dir_prefix, mrc_path)

        if omezarr_path := metadata.get("omezarr_dir"):
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

        return extra_data

    @classmethod
    def get_item(cls, run_id: int, run: RunDBImporter, config: DBImportConfig) -> "TiltSeriesDBImporter":
        ts_dir_path = cls.join_path(run.dir_prefix, "TiltSeries")
        for ts_prefix in config.find_subdirs_with_files(ts_dir_path, "tiltseries_metadata.json"):
            return cls(run_id, ts_prefix, run, config)
