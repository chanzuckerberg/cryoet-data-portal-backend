import os
from typing import TYPE_CHECKING

from common.config import DepositionImportConfig
from common.metadata import TiltSeriesMetadata
from importers.base_importer import BaseImporter, VolumeImporter
from importers.frames import FramesImporter
import subprocess

if TYPE_CHECKING:
    from importers.run import RunImporter
else:
    RunImporter = "RunImporter"


class GainImporter(BaseImporter):
    type_key = "gain"

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