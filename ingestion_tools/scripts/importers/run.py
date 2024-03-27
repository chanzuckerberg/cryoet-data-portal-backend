import os
from typing import TYPE_CHECKING, Any

from common.config import DepositionImportConfig
from common.metadata import RunMetadata
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.dataset import DatasetImporter
else:
    DatasetImporter = "DatasetImporter"


class RunImporter(BaseImporter):
    type_key = "run"

    def __init__(
        self,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ):
        super().__init__(*args, **kwargs)
        # Backwards compatibility
        if not self.name:
            self.name = self.config.run_name_regex.match(os.path.basename(self.path))[1]

    def import_run_metadata(self) -> None:
        dest_run_metadata = self.get_metadata_path()
        metadata = RunMetadata(self.config.fs, self.config.deposition_id, self.config.run_template)
        merge_data = {"run_name": self.name}
        metadata.write_metadata(dest_run_metadata, merge_data)

    @classmethod
    def find_runs(cls, config: DepositionImportConfig, dataset: DatasetImporter) -> list[Any]:
        run_path = os.path.join(config.input_path, config.run_glob)
        responses = []
        for fname in config.fs.glob(run_path):
            if config.run_regex.search(fname):
                responses.append(cls(config=config, parent=dataset, path=fname))
        return responses
