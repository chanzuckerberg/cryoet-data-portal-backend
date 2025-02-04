import os
from typing import Any

from common.finders import MultiSourceFileFinder
from common.metadata import FrameMetadata
from importers.base_importer import BaseFileImporter
from importers.collection_metadata import CollectionMetadataImporter


class FrameImporter(BaseFileImporter):
    type_key = "frame"
    plural_key = "frames"
    finder_factory = MultiSourceFileFinder
    has_metadata = True
    dir_path = "{dataset_name}/{run_name}/Frames"
    metadata_path = os.path.join(dir_path, "frames_metadata.json")

    def __init__(self, *args, file_paths: dict[str, str], **kwargs):
        super().__init__(*args, **kwargs)
        self.file_paths = file_paths

    def get_frame_count(self) -> int:
        return len(self.file_paths)

    def get_dest_filename(self, path: str) -> str | None:
        if not path:
            return None
        return os.path.join(self.get_output_path(), os.path.basename(path))

    def import_item(self) -> None:
        if not self.is_import_allowed() or self.is_default_source():
            print(f"Skipping import of {self.name}")
            return

        for path in self.file_paths.values():
            print(f"Copying {path}")
            self.config.fs.copy(path, self.get_dest_filename(path))

    def import_metadata(self) -> None:
        base_metadata = self.get_base_metadata()
        dose_rate = base_metadata.get("dose_rate")
        if not dose_rate:
            raise Exception(f"Invalid dose rate for Frames: {dose_rate}")

        collection_md = CollectionMetadataImporter.get_importer(self.config, **self.parents)
        extra_metadata = {
            "frames": self.get_frame_metadata(float(dose_rate), collection_md),
            "frames_acquisition_file": self.config.to_formatted_path(collection_md.get_destination_path()),
        }

        metadata = FrameMetadata(self.config.fs, self.get_deposition().name, base_metadata)
        metadata.write_metadata(self.get_metadata_path(), extra_metadata)

    def is_default_source(self) -> bool:
        return "default" in self.file_paths

    def get_frame_output_path_by_name(self) -> dict[str, str]:
        if self.is_default_source():
            return {}
        return {
            os.path.basename(path): self.config.to_formatted_path(self.get_dest_filename(path))
            for path in self.file_paths
        }

    def get_frame_metadata(self, dose_rate: float, collection_md: CollectionMetadataImporter) -> list[dict[str, Any]]:
        frame_path_by_name = self.get_frame_output_path_by_name()
        mdoc = collection_md.get_output_data()
        frames = []
        accumulated_dose = 0
        for section in mdoc.section_data:
            exposure_time = section.ExposureTime
            exposure_dose = exposure_time * dose_rate
            frame_name = section.SubFramePath.name if section.SubFramePath else None
            entry = {
                "acquisition_order": section.ZValue,
                "accumulated_dose": accumulated_dose,
                "exposure_dose": exposure_dose,
                "path": frame_path_by_name.get(frame_name),
            }
            frames.append(entry)
            accumulated_dose += exposure_dose
        return frames
