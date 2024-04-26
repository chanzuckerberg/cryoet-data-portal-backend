from typing import TYPE_CHECKING

from common.finders import DefaultImporterFactory
from common.metadata import TiltSeriesMetadata
from importers.base_importer import VolumeImporter
from importers.frame import FrameImporter

if TYPE_CHECKING:
    from importers.run import RunImporter
else:
    RunImporter = "RunImporter"


class TiltSeriesImporter(VolumeImporter):
    type_key = "tiltseries"
    plural_key = "tiltseries"
    finder_factory = DefaultImporterFactory
    dependencies = ["run"]
    has_metadata = True

    def import_tiltseries(self, write_mrc: bool = True, write_zarr: bool = True) -> None:
        _ = self.scale_mrcfile(
            scale_z_axis=False,
            write_mrc=write_mrc,
            write_zarr=write_zarr,
            voxel_spacing=self.get_pixel_spacing(),
        )

    def get_frames_count(self) -> int:
        return len(FrameImporter.find_all_frames(self.config, self.get_run()))

    def import_metadata(self, write: bool) -> None:
        dest_ts_metadata = self.get_metadata_path()
        merge_data = self.load_extra_metadata()
        merge_data["frames_count"] = self.get_frames_count()
        base_metadata = self.get_base_metadata()
        merge_data["pixel_spacing"] = self.get_pixel_spacing()
        metadata = TiltSeriesMetadata(self.config.fs, self.config.deposition_id, base_metadata)
        if write:
            metadata.write_metadata(dest_ts_metadata, merge_data)

    def get_pixel_spacing(self) -> float:
        pixel_spacing = self.get_base_metadata().get("pixel_spacing")
        if pixel_spacing:
            return float(pixel_spacing)
        return round(self.get_voxel_size().item(), 3)

    def mrc_header_mapper(self, header) -> None:
        header.ispg = 0
        header.mz = 1
        header.cella.z = 1 * self.get_pixel_spacing()
