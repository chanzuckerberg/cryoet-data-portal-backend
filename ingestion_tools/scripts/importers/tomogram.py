import os
from typing import Any

from common.finders import DefaultImporterFactory
from common.image import VolumeInfo, get_volume_info
from common.metadata import TomoMetadata
from common.normalize_fields import normalize_fiducial_alignment
from importers.base_importer import VolumeImporter
from importers.key_image import KeyImageImporter


class TomogramImporter(VolumeImporter):
    type_key = "tomogram"
    plural_key = "tomograms"
    finder_factory = DefaultImporterFactory
    cached_find_results: dict[str, Any] = {}
    has_metadata = True
    dir_path = "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/CanonicalTomogram"
    metadata_path = (
        "{dataset_name}/{run_name}/Tomograms/VoxelSpacing{voxel_spacing_name}/CanonicalTomogram/tomogram_metadata.json"
    )

    def import_item(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return
        self.scale_mrcfile(
            write_mrc=self.config.write_mrc,
            write_zarr=self.config.write_zarr,
            voxel_spacing=self.get_voxel_spacing().as_float(),
        )

    def import_metadata(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return
        dest_tomo_metadata = self.get_metadata_path()
        merge_data = self.load_extra_metadata()
        parent_args = dict(self.parents)
        parent_args["tomogram"] = self
        key_photo_types = ["snapshot", "thumbnail"]
        merge_data["key_photo"] = {}
        for keyimage in KeyImageImporter.finder(self.config, **parent_args):
            if keyimage.name in key_photo_types:
                merge_data["key_photo"][keyimage.name] = keyimage.find_key_image_path(keyimage.name)
        base_metadata = self.get_base_metadata()
        merge_data["voxel_spacing"] = self.get_voxel_spacing().as_float()
        # Enforce our schema for these values.
        base_metadata["fiducial_alignment_status"] = normalize_fiducial_alignment(
            base_metadata.get("fiducial_alignment_status"),
        )

        metadata = TomoMetadata(self.config.fs, self.get_deposition().name, base_metadata)
        metadata.write_metadata(dest_tomo_metadata, merge_data)

    def get_source_volume_info(self) -> VolumeInfo:
        return get_volume_info(self.config.fs, self.volume_filename)

    @classmethod
    def get_name_and_path(cls, metadata: dict, name: str, path: str, results: dict[str, str]) -> [str, str, dict]:
        filename = metadata.get("omezarr_dir")
        complete_path = os.path.join(os.path.dirname(path), filename)
        return filename, complete_path, {filename: complete_path}
