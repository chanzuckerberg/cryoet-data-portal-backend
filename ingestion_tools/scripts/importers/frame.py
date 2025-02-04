import os

from common.finders import MultiSourceFileFinder
from importers.base_importer import BaseFileImporter


class FrameImporter(BaseFileImporter):
    type_key = "frame"
    plural_key = "frames"
    finder_factory = MultiSourceFileFinder
    has_metadata = False
    dir_path = "{dataset_name}/{run_name}/Frames"

    def __init__(self, *args, file_paths: dict[str, str], **kwargs):
        super().__init__(*args, **kwargs)
        self.file_paths = file_paths

    def get_dest_filename(self, path: str) -> str | None:
        if not path:
            return None
        return os.path.join(self.get_output_path(), os.path.basename(path))

    def import_item(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return

        for path in self.file_paths.values():
            self.config.fs.copy(path, self.get_dest_filename(path))
