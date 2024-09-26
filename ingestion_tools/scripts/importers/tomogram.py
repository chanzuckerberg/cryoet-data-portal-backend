import os
from typing import Any

from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from common.id_helper import IdentifierHelper
from common.image import VolumeInfo, get_volume_info
from common.metadata import TomoMetadata
from common.normalize_fields import normalize_fiducial_alignment
from importers.base_importer import VolumeImporter
from importers.key_image import KeyImageImporter


class TomogramIdentifierHelper(IdentifierHelper):
    @classmethod
    def _get_container_key(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        return parents["voxel_spacing"].get_output_path()

    @classmethod
    def _get_metadata_glob(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        voxel_spacing = parents["voxel_spacing"]
        tomogram_dir_path = config.resolve_output_path("tomogram", voxel_spacing)
        return os.path.join(tomogram_dir_path, "*tomogram_metadata.json")

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
                metadata.get("alignment_metadata_path", kwargs.get("alignment_metadata_path")),
                metadata.get("reconstruction_method", ""),
                metadata.get("processing", ""),
                str(metadata.get("deposition_id", int(parents["deposition"].name))),
            ],
        )


class TomogramImporter(VolumeImporter):
    type_key = "tomogram"
    plural_key = "tomograms"
    finder_factory = DefaultImporterFactory
    cached_find_results: dict[str, Any] = {}
    has_metadata = True

    def __init__(
        self,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        parents: dict[str, Any],
    ):
        super().__init__(config=config, metadata=metadata, name=name, path=path, parents=parents)
        self.alignment_metadata_path = self.get_alignment_metadata_path()
        self.identifier = TomogramIdentifierHelper.get_identifier(
            config,
            self.get_base_metadata(),
            self.parents,
            alignment_metadata_path=self.alignment_metadata_path,
        )

    def import_item(self) -> None:
        self.scale_mrcfile(
            write_mrc=self.config.write_mrc,
            write_zarr=self.config.write_zarr,
            voxel_spacing=self.get_voxel_spacing().as_float(),
        )

    def dir_path(self) -> str:
        output_dir = self.config.resolve_output_path(self.type_key, self)
        return os.path.join(output_dir, f"{self.identifier}")

    def get_output_path(self) -> str:
        return f"{self.dir_path()}-{self.get_run().name}"

    def get_metadata_path(self) -> str:
        return f"{self.dir_path()}-tomogram_metadata.json"

    def import_metadata(self) -> None:
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
        merge_data["alignment_metadata_path"] = self.alignment_metadata_path
        metadata = TomoMetadata(self.config.fs, self.get_deposition().name, base_metadata)
        metadata.write_metadata(dest_tomo_metadata, merge_data)

    def get_source_volume_info(self) -> VolumeInfo:
        return get_volume_info(self.config.fs, self.volume_filename)

    def get_alignment_metadata_path(self) -> str:
        from importers.alignment import AlignmentImporter

        for alignment in AlignmentImporter.finder(self.config, **self.parents):
            return alignment.get_metadata_path()
        # TODO: This should be an error, but we need to fix the data first.
        return None
