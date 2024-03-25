import os
from typing import TYPE_CHECKING, Any

from common.config import DataImportConfig
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
        path: str,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ):
        super().__init__(*args, **kwargs)
        self.run_path = path
        self.run_name = self.config.run_name_regex.match(os.path.basename(path))[1]
        if voxel_spacing := self.config.expand_string(
            self.run_name,
            self.config.tomogram_template.get("voxel_spacing"),
        ):
            self.set_voxel_spacing(float(voxel_spacing))
        else:
            self.voxel_spacing = None

    def set_voxel_spacing(self, voxel_spacing: float) -> None:
        self.voxel_spacing = "{:.3f}".format(round(voxel_spacing, 3))

    def import_run_metadata(self) -> None:
        dest_run_metadata = self.get_metadata_path()
        metadata = RunMetadata(self.config.fs, self.config.deposition_id, self.config.run_template)
        merge_data = {"run_name": self.run_name}
        metadata.write_metadata(dest_run_metadata, merge_data)

    @classmethod
    def find_runs(cls, config: DataImportConfig, dataset: DatasetImporter) -> list[Any]:
        run_path = os.path.join(config.input_path, config.run_glob)
        responses = []
        for fname in config.fs.glob(run_path):
            if config.run_regex.search(fname):
                responses.append(cls(config=config, parent=dataset, path=fname))
        return responses
