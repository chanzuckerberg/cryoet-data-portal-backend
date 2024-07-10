import os
import subprocess

from common.finders import DefaultImporterFactory
from importers.base_importer import BaseImporter


class GainImporter(BaseImporter):
    type_key = "gain"
    plural_key = "gains"
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def import_item(self) -> None:
        fs = self.config.fs
        item = self.path
        output_filename = self.get_output_path()
        if item.endswith(".dm4"):
            local_input = fs.localreadable(item)
            local_output = fs.localwritable(output_filename + ".mrc")
            subprocess.check_output(["/usr/local/IMOD/bin/dm2mrc", local_input, local_output])
            fs.push(local_output)
        else:
            _, extension = os.path.splitext(item)
            fs.copy(item, f"{output_filename}.{extension}")
