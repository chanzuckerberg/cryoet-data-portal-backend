import os
from typing import TYPE_CHECKING

from common.config import DataImportConfig
from common.metadata import TiltSeriesMetadata
from importers.base_importer import BaseImporter, VolumeImporter
from importers.frames import FramesImporter

if TYPE_CHECKING:
    from importers.run import RunImporter
else:
    RunImporter = "RunImporter"


class RawTiltImporter(BaseImporter):
    type_key = "tiltseries"

    def import_rawtilts(self):
        # Copy rawtilt files and/or xf files and/or tlt files and/or mdoc files to their dest
        run = self.get_run()
        # TODO - We should probably instantiate this class for each file in our list of rawtilt files
        # but we're cheating and importing them all through a single instance. If we need to expand
        # the functionality we support for rawtilts we should refactor this.
        for file_glob in self.config.rawtlt_files:
            for item in self.config.glob_files(run, file_glob):
                output_file = os.path.join(self.get_output_path(), os.path.basename(item))
                self.config.fs.copy(item, output_file)

    @classmethod
    def find_rawtilts(cls, config: DataImportConfig, run: RunImporter) -> list["RawTiltImporter"]:
        if not config.rawtlt_files:
            print(f"No tiltseries raw files for {config.dataset_template.get('dataset_identifier')}")
            return []
        return [cls(config=config, parent=run)]


class TiltSeriesImporter(VolumeImporter):
    type_key = "tiltseries"

    def import_tiltseries(self, write_mrc: bool = True, write_zarr: bool = True):
        _ = self.scale_mrcfile(
            scale_z_axis=False, write_mrc=write_mrc, write_zarr=write_zarr, voxel_spacing=self.get_pixel_spacing(),
        )

    def get_frames_count(self) -> int:
        return len(FramesImporter.find_all_frames(self.config, self.get_run()))

    def import_metadata(self, write: bool):
        dest_ts_metadata = self.get_metadata_path()
        merge_data = self.load_extra_metadata()
        merge_data["frames_count"] = self.get_frames_count()
        base_metadata = self.get_base_metadata()
        merge_data["pixel_spacing"] = self.get_pixel_spacing()
        metadata = TiltSeriesMetadata(self.config.fs, base_metadata)
        if write:
            metadata.write_metadata(dest_ts_metadata, merge_data)

    @classmethod
    def find_tiltseries(cls, config: DataImportConfig, run: RunImporter):
        if not config.tiltseries_glob:
            print(f"No tiltseries for {config.dataset_template.get('dataset_identifier')}")
            return []
        importers = []
        for item in config.glob_files(run, config.tiltseries_glob):
            if config.ts_name_regex and not config.ts_name_regex.match(item):
                continue
            importers.append(cls(config=config, parent=run, path=item))

        return importers

    def get_pixel_spacing(self):
        pixel_spacing = self.get_base_metadata().get("pixel_spacing")
        if pixel_spacing:
            return float(pixel_spacing)
        return round(self.get_voxel_size().item(), 3)

    def mrc_header_mapper(self, header):
        header.ispg = 0
        header.mz = 1
        header.cella.z = 1 * self.get_pixel_spacing()
