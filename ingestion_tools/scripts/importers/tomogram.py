import os
import re
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
        return "-".join(["tomogram", parents["run"].get_output_path()])

    @classmethod
    def _get_metadata_glob(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        voxel_spacing = parents["voxel_spacing"]
        tomogram_dir_path = config.resolve_output_path("tomogram_metadata", voxel_spacing, {"tomogram_id": "*"})
        search_path = re.sub(r"/VoxelSpacing[0-9.]+/", "/VoxelSpacing*/", tomogram_dir_path)
        return search_path

    @classmethod
    def _generate_hash_key(
        cls,
        container_key: str,
        metadata: dict[str, Any],
        parents: dict[str, Any],
        *args,
        **kwargs,
    ) -> str:
        voxel_spacing = metadata.get("voxel_spacing")
        # Handles the case where voxel_spacing in the config metadata is a formatted string
        if not voxel_spacing or isinstance(voxel_spacing, str) and not voxel_spacing.isdigit():
            voxel_spacing = parents["voxel_spacing"].name
        elif isinstance(voxel_spacing, float):
            voxel_spacing = f"{voxel_spacing:.3f}"
        return "-".join(
            [
                container_key,
                str(voxel_spacing),
                metadata.get("alignment_metadata_path", kwargs.get("alignment_metadata_path", "")),
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
    dir_path = "{dataset_name}/{run_name}/Reconstructions/VoxelSpacing{voxel_spacing_name}/Tomograms/{tomogram_id}"
    metadata_path = os.path.join(dir_path, "tomogram_metadata.json")

    def __init__(
        self,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        allow_imports: bool,
        parents: dict[str, Any],
        alignment_metadata_path: str = None,
    ):
        super().__init__(
            config=config,
            metadata=metadata,
            name=name,
            path=path,
            parents=parents,
            allow_imports=allow_imports,
        )

        self.alignment_metadata_path = config.to_formatted_path(alignment_metadata_path or self.get_alignment_metadata_path())
        self.identifier = TomogramIdentifierHelper.get_identifier(
            config,
            self.get_base_metadata(),
            self.parents,
            alignment_metadata_path=self.alignment_metadata_path,
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

    def get_identifier(self) -> int:
        return self.identifier

    def import_metadata(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name} metadata")
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
        merge_data["alignment_metadata_path"] = self.alignment_metadata_path
        merge_data["neuroglancer_config_path"] = self.config.to_formatted_path(self.get_neuroglancer_config_path())
        metadata = TomoMetadata(self.config.fs, self.get_deposition().name, base_metadata)
        metadata.write_metadata(dest_tomo_metadata, merge_data)

    def get_source_volume_info(self) -> VolumeInfo:
        return get_volume_info(self.config.fs, self.volume_filename)

    def get_alignment_metadata_path(self) -> str:
        from importers.alignment import AlignmentImporter

        for alignment in AlignmentImporter.finder(self.config, **self.parents):
            return alignment.get_metadata_path()
        # TODO: As all tomograms need to be associated to an alignment this should be an error, but we need to fix the
        #  data first.
        return None

    def get_neuroglancer_config_path(self) -> str | None:
        if self.metadata.get("is_visualization_default"):
            return self.config.resolve_output_path("viz_config", self)
        return None

    @classmethod
    def get_name_and_path(cls, metadata: dict, name: str, path: str, results: dict[str, str]) -> [str, str, dict]:
        filename = metadata.get("omezarr_dir")
        complete_path = os.path.join(os.path.dirname(path), filename)
        return filename, complete_path, {filename: complete_path}
