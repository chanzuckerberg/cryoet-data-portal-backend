import os
from typing import Any

from common.finders import DefaultImporterFactory
from common.metadata import RunMetadata
from importers.base_importer import BaseImporter


class RunImporter(BaseImporter):
    type_key = "run"
    plural_key = "runs"
    finder_factory = DefaultImporterFactory
    has_metadata = True

    def __init__(
        self,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ):
        super().__init__(*args, **kwargs)
        # Backwards compatibility
        if not self.name:
            self.name = self.config.run_name_regex.match(os.path.basename(self.path))[1]

    def import_item(self) -> None:
        pass

    def import_metadata(self) -> None:
        dest_run_metadata = self.get_metadata_path()
        print(dest_run_metadata)
        metadata = RunMetadata(self.config.fs, self.get_deposition().name, self.metadata)
        merge_data = {"run_name": self.name}
        metadata.write_metadata(dest_run_metadata, merge_data)
