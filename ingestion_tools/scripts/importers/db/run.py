from typing import Any, Iterator

from common import db_models
from importers.db.base_importer import BaseDBImporter, DBImportConfig
from importers.db.dataset import DatasetDBImporter


class RunDBImporter(BaseDBImporter):
    def __init__(
        self, dataset_id: int, dir_prefix: str, parent: DatasetDBImporter, config: DBImportConfig
    ):
        self.dataset_id = dataset_id
        self.dir_prefix = dir_prefix
        self.parent = parent
        self.config = config
        self.metadata = config.load_key_json(self.get_metadata_file_path())

    def get_metadata_file_path(self) -> str:
        return self.join_path(self.dir_prefix, "run_metadata.json")

    def get_data_map(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "name": ["run_name"],
            "s3_prefix": self.join_path(self.config.s3_prefix, self.dir_prefix),
            "https_prefix": self.join_path(self.config.https_prefix, self.dir_prefix),
        }

    def get_id_fields(self) -> list[str]:
        return ["dataset_id", "name"]

    def get_db_model_class(self) -> type:
        return db_models.Run

    @classmethod
    def get_item(
        cls, dataset_id: int, dataset: DatasetDBImporter, config: DBImportConfig
    ) -> "Iterator[RunDBImporter]":
        return [
            cls(dataset_id, run_prefix, dataset, config)
            for run_prefix in config.find_subdirs_with_files(dataset.dir_prefix, "run_metadata.json")
        ]
