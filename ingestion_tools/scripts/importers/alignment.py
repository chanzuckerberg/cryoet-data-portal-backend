import os.path
from typing import TYPE_CHECKING, Any

from common.alignment_converter import alignment_converter_factory
from common.config import DepositionImportConfig
from common.finders import MultiSourceFileGlobFinder
from common.id_helper import IdentifierHelper
from common.metadata import AlignmentMetadata
from importers.base_importer import BaseFileImporter

if TYPE_CHECKING:
    TomogramImporter = "TomogramImporter"
else:
    from importers.tomogram import TomogramImporter


class AlignmentIdentifierHelper(IdentifierHelper):
    @classmethod
    def _get_container_key(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        return parents["run"].get_output_path()

    @classmethod
    def _get_metadata_glob(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        run = parents["run"]
        alignment_dir_path = config.resolve_output_path("alignment", run)
        return os.path.join(alignment_dir_path, "*alignment_metadata.json")

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


class AlignmentImporter(BaseFileImporter):
    type_key = "alignment"
    plural_key = "alignments"
    finder_factory = MultiSourceFileGlobFinder
    has_metadata = True
    written_metadata_files = set()

    def __init__(
        self,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        parents: dict[str, Any],
        file_paths: dict[str, str],
    ):
        super().__init__(config, metadata, name, path, parents)
        self.identifier = AlignmentIdentifierHelper.get_identifier(config, metadata, parents)
        self.file_paths = file_paths
        self.converter = alignment_converter_factory(
            config,
            metadata,
            list(file_paths.keys()),
            parents,
            self.get_output_path(),
        )

    def import_metadata(self) -> None:
        metadata_path = self.get_metadata_path()
        try:
            meta = AlignmentMetadata(self.config.fs, self.get_deposition().name, self.get_base_metadata())
            meta.write_metadata(metadata_path, self.get_extra_metadata())
            self.written_metadata_files.add(metadata_path)
        except IOError:
            print("Skipping creating metadata for default alignment with no source tomogram")

    def import_item(self) -> None:
        if self.is_default_alignment() or not self.is_valid():
            print(
                f"Skipping importing alignment with path {self.file_paths} as it is either a default alignment or "
                "doesn't have dimension data",
            )
            return
        for path in self.file_paths.values():
            dest_filename = self.get_dest_filename(path)
            self.config.fs.copy(path, dest_filename)

    def get_output_path(self) -> str:
        output_directory = super().get_output_path()
        return os.path.join(output_directory, f"{self.identifier}-")

    def get_dest_filename(self, path: str) -> str | None:
        if not path:
            return None
        output_dir = self.get_output_path()
        return f"{output_dir}{os.path.basename(path)}"

    def get_metadata_path(self) -> str:
        return self.get_output_path() + "alignment_metadata.json"

    def get_extra_metadata(self) -> dict:
        extra_metadata = {
            "per_section_alignment_parameters": self.converter.get_per_section_alignment_parameters(),
            "alignment_path": self.converter.get_alignment_path(),
            "tilt_path": self.converter.get_tilt_path(),
            "tiltx_path": self.converter.get_tiltx_path(),
        }
        if "volume_dimension" not in self.metadata:
            extra_metadata["volume_dimension"] = self.get_tomogram_volume_dimension()
        for key, value in self.get_default_metadata().items():
            if key not in self.metadata:
                extra_metadata[key] = value
        return extra_metadata

    def get_tomogram_volume_dimension(self) -> dict:
        for tomogram in TomogramImporter.finder(self.config, **self.parents):
            return tomogram.get_source_volume_info().get_dimensions()

        # If no source tomogram is found don't create a default alignment metadata file.
        raise IOError("No source tomogram found for creating default alignment")

    def is_default_alignment(self) -> bool:
        return "default" in self.file_paths

    def is_valid(self) -> bool:
        volume_dim = self.metadata.get("volume_dimension", {})
        return (
            all(volume_dim.get(dim) for dim in "xyz")
            or next(TomogramImporter.finder(self.config, **self.parents), None) is not None
        )

    @classmethod
    def get_default_config(cls) -> list[dict]:
        return [{"metadata": cls.get_default_metadata(), "sources": [{"literal": {"value": ["default"]}}]}]

    @classmethod
    def get_default_metadata(cls) -> dict[str, Any]:
        return {
            "affine_transformation_matrix": [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ],
            "alignment_type": "GLOBAL",
            "is_canonical": False,
            "volume_offset": {"x": 0, "y": 0, "z": 0},
            "tilt_offset": 0,
            "x_rotation_offset": 0,
        }
