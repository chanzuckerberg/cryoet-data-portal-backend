from typing import TYPE_CHECKING, Any

from common.config import DepositionImportConfig
from common.metadata import TomoMetadata
from common.normalize_fields import normalize_fiducial_alignment
from importers.base_importer import VolumeImporter
from importers.key_image import KeyImageImporter
from importers.voxel_spacing import VoxelSpacingImporter
from common.finders import DefaultImporterFactory

if TYPE_CHECKING:
    from importers.run import RunImporter
else:
    RunImporter = "RunImporter"


class TomogramImporter(VolumeImporter):
    type_key = "tomogram"
    finder_factory = DefaultImporterFactory
    cached_find_results: dict[str, Any] = {}
    dependencies = ["voxel_spacing"]
    has_metadata = True

    def get_voxel_spacing(self) -> float:
        return float(self.parent.name)

    def import_tomogram(self, write_mrc: bool = True, write_zarr: bool = True) -> None:
        if self.config.tomo_format != "mrc":
            raise NotImplementedError("implement handling for other tomo input formats!")
        _ = self.scale_mrcfile(write_mrc=write_mrc, write_zarr=write_zarr, voxel_spacing=self.get_voxel_spacing())

    def import_metadata(self, write: bool) -> None:
        dest_tomo_metadata = self.get_metadata_path()
        merge_data = self.load_extra_metadata()
        key_image_importer = KeyImageImporter(self.config, parent=self)
        merge_data["key_photo"] = {
            "snapshot": key_image_importer.find_key_image_path("snapshot"),
            "thumbnail": key_image_importer.find_key_image_path("thumbnail"),
        }
        base_metadata = self.get_base_metadata()
        if base_metadata.get("voxel_spacing"):
            base_metadata["voxel_spacing"] = float(base_metadata["voxel_spacing"])
        else:
            merge_data["voxel_spacing"] = round(self.get_voxel_spacing(), 3)
        # Enforce our schema for these values.
        base_metadata["fiducial_alignment_status"] = normalize_fiducial_alignment(
            base_metadata.get("fiducial_alignment_status"),
        )

        metadata = TomoMetadata(self.config.fs, self.config.deposition_id, base_metadata)
        if write:
            metadata.write_metadata(dest_tomo_metadata, merge_data)
