import os
from typing import TYPE_CHECKING, Any

from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter

if TYPE_CHECKING:
    AlignmentIdentifierHelper = "AlignmentIdentifierHelper"
else:
    from importers.alignment import AlignmentIdentifierHelper


class TiltImporter(BaseFileImporter):
    type_key = "tilt"
    plural_key = "tilts"
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def __init__(
        self,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        parents: dict[str, Any],
    ):
        super().__init__(config, metadata, name, path, parents)
        self.identifier = AlignmentIdentifierHelper.get_identifier(config, {}, parents)

    def get_dest_filename(self) -> str:
        output_dir = self.get_output_path()
        return f"{output_dir}{os.path.basename(self.path)}"

    def get_output_path(self) -> str:
        output_directory = super().get_output_path()
        return os.path.join(output_directory, f"{self.identifier}-")
