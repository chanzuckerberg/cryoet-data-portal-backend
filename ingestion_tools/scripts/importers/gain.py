import subprocess

from common.finders import DefaultImporterFactory
from importers.base_importer import BaseImporter


class GainImporter(BaseImporter):
    type_key = "gains"
    finder_factory = DefaultImporterFactory
    dependencies = ["run"]
    has_metadata = False

    def import_item(self) -> None:
        fs = self.config.fs
        item = self.path
        output_filename = self.get_output_path()
        if item.endswith(".dm4"):
            local_input = fs.localreadable(item)
            local_output = fs.localwritable(output_filename)
            subprocess.check_output(["/usr/local/IMOD/bin/dm2mrc", local_input, local_output])
            fs.push(local_output)
        else:
            fs.copy(item, output_filename)
