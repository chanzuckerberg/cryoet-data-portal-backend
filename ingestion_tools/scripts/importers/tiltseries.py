import os.path
from typing import Any

from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from common.id_helper import IdentifierHelper
from common.metadata import TiltSeriesMetadata
from importers.base_importer import VolumeImporter
from importers.frame import FrameImporter


class TiltSeriesIdentifierHelper(IdentifierHelper):
    @classmethod
    def _get_container_key(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        return parents["run"].get_output_path()

    @classmethod
    def _get_metadata_glob(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        run = parents["run"]
        tiltseries_dir_path = config.resolve_output_path("tiltseries", run)
        return os.path.join(tiltseries_dir_path, "*tiltseries_metadata.json")

    @classmethod
    def _generate_hash_key(
        cls,
        container_key: str,
        metadata: dict[str, Any],
        parents: dict[str, Any],
        *args,
        **kwargs,
    ) -> str:
        return "-".join(
            [
                container_key,
                str(metadata.get("deposition_id", int(parents["deposition"].name))),
            ],
        )


class TiltSeriesImporter(VolumeImporter):
    type_key = "tiltseries"
    plural_key = "tiltseries"
    finder_factory = DefaultImporterFactory
    has_metadata = True
    dir_path = "{dataset_name}/{run_name}/TiltSeries"
    metadata_path = "{dataset_name}/{run_name}/TiltSeries/{{identifier}}-tiltseries_metadata.json"

    def __init__(
        self,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        allow_imports: bool,
        parents: dict[str, Any],
    ):
        super().__init__(
            config=config, metadata=metadata, name=name, path=path, parents=parents, allow_imports=allow_imports,
        )
        self.identifier = TiltSeriesIdentifierHelper.get_identifier(config, self.get_base_metadata(), self.parents)

    def get_metadata_path(self) -> str:
        return super().get_metadata_path().format(identifier=self.identifier)

    def import_item(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return
        _ = self.scale_mrcfile(
            scale_z_axis=False,
            write_mrc=self.config.write_mrc,
            write_zarr=self.config.write_zarr,
            voxel_spacing=self.get_pixel_spacing(),
        )

    def get_frames_count(self) -> int:
        parent_args = dict(self.parents)
        parent_args["tiltseries"] = self
        num_frames = 0
        for _ in FrameImporter.finder(self.config, **parent_args):
            num_frames += 1
        return num_frames

    def import_metadata(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return
        dest_ts_metadata = self.get_metadata_path()
        merge_data = self.load_extra_metadata()
        merge_data["frames_count"] = self.get_frames_count()
        base_metadata = self.get_base_metadata()
        merge_data["pixel_spacing"] = self.get_pixel_spacing()
        metadata = TiltSeriesMetadata(self.config.fs, self.get_deposition().name, base_metadata)
        metadata.write_metadata(dest_ts_metadata, merge_data)

    def get_pixel_spacing(self) -> float:
        pixel_spacing = self.get_base_metadata().get("pixel_spacing")
        if pixel_spacing:
            return float(pixel_spacing)
        return round(self.get_voxel_size(), 3)

    def mrc_header_mapper(self, header) -> None:
        header.ispg = 0
        header.mz = 1
        header.cella.z = 1 * self.get_pixel_spacing()

    @classmethod
    def get_name_and_path(cls, metadata: dict, name: str, path: str, results: dict[str, str]) -> [str, str, dict]:
        filename = metadata.get("omezarr_dir")
        complete_path = os.path.join(os.path.dirname(path), filename)
        return filename, complete_path, {filename: complete_path}
