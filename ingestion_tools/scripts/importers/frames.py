import os
import subprocess
from typing import TYPE_CHECKING

from common.config import DataImportConfig

from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.run import RunImporter
else:
    RunImporter = "RunImporter"


class FramesImporter(BaseImporter):
    type_key = "frames"

    def import_frames(self, write: bool = True):
        run = self.get_run()
        config = self.config
        fs = self.config.fs
        output_dir = self.get_output_path()
        for item in self.find_all_frames(config, run):
            dest_filename = os.path.join(output_dir, os.path.basename(item))
            fs.copy(item, dest_filename)
        if not config.gain_glob:
            return
        for item in self.find_all_gains(config, run):
            if item.endswith(".dm4"):
                local_input = fs.localreadable(item)
                local_output = fs.localwritable(os.path.join(output_dir, f"{run.run_name}_gain.mrc"))
                subprocess.check_output(["/usr/local/IMOD/bin/dm2mrc", local_input, local_output])
                fs.push(local_output)
            else:
                dest_filename = os.path.join(output_dir, f"{run.run_name}_gain.mrc")
                fs.copy(item, dest_filename)

    @classmethod
    def find_frames(cls, config: DataImportConfig, run: RunImporter) -> list["FramesImporter"]:
        if not config.frames_glob:
            print(f"No frames for {config.dataset_template.get('dataset_identifier')}")
            return []
        importer = cls(config=config, parent=run)
        return [importer]

    @classmethod
    def find_all_frames(cls, config: DataImportConfig, run: RunImporter):
        return cls.find_files(config.frames_glob, config, run)

    @classmethod
    def find_all_gains(cls, config: DataImportConfig, run: RunImporter):
        return cls.find_files(config.gain_glob, config, run)

    @classmethod
    def find_files(cls, glob: str, config: DataImportConfig, run: RunImporter):
        if not glob:
            return []
        if config.run_to_frame_map:
            glob = glob.format(**run.get_glob_vars())
        return config.glob_files(run, glob)
