import os
import subprocess

from common.finders import DefaultImporterFactory
from importers.base_importer import BaseImporter


class GainImporter(BaseImporter):
    type_key = "gain"
    plural_key = "gains"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = "{dataset_name}/{run_name}/Gains"

    def import_item(self) -> None:
        fs = self.config.fs
        item = self.path
        source_file_name = os.path.basename(item)
        output_dir = self.get_output_path()
        if item.endswith(".dm4"):
            dest_file_name = os.path.splitext(source_file_name)[0] + ".mrc"
            local_input = fs.localreadable(item)
            local_output = fs.localwritable(os.path.join(output_dir, dest_file_name))
            subprocess.check_output(["/usr/local/IMOD/bin/dm2mrc", local_input, local_output])
            fs.push(local_output)
        else:
            dest_file_path = os.path.join(output_dir, source_file_name)
            fs.copy(item, dest_file_path)
