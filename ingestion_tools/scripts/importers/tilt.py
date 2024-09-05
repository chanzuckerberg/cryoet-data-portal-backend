import os

from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter


class TiltImporter(BaseFileImporter):
    type_key = "tilt"
    plural_key = "tilts"
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def get_dest_filename(self) -> str:
        output_dir = self.get_output_path()
        return f"{output_dir}{os.path.basename(self.path)}"

    def get_output_path(self) -> str:
        output_directory = super().get_output_path()
        return os.path.join(output_directory, "id-")
