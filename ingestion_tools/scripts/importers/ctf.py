import os

from common.ctf_converter import CTFInfo, ctf_converter_factory
from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter


class CtfImporter(BaseFileImporter):
    type_key = "ctf"
    plural_key = "ctfs"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = "{dataset_name}/{run_name}/TiltSeries/{tiltseries_id}"

    def get_destination_path(self) -> str:
        filename = f"{self.parents['run'].name}_{self.metadata.get('format', 'unknown')}_ctf.txt"
        return os.path.join(self.get_output_path(), filename)

    def get_output_data(self) -> list[CTFInfo]:
        path = self.get_destination_path()
        ctf_factory = ctf_converter_factory(self.metadata, self.config, path)
        return ctf_factory.get_ctf_info()
