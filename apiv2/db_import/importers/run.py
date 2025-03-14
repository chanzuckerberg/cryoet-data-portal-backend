from typing import Any, Iterator

from database.models import Run

from db_import.common.config import DBImportConfig
from db_import.importers.base_importer import (
    BaseDBImporter,
    StaleDeletionDBImporter,
    StaleParentDeletionDBImporter,
)
from db_import.importers.dataset import DatasetDBImporter
from platformics.database.models import Base


class RunDBImporter(BaseDBImporter):
    def __init__(self, dataset_id: int, dir_prefix: str, parent: DatasetDBImporter, config: DBImportConfig):
        self.dataset_id = dataset_id
        self.dir_prefix = dir_prefix
        self.parent = parent
        self.config = config
        self.metadata = config.load_key_json(self.get_metadata_file_path())

    def get_metadata_file_path(self) -> str:
        return self.join_path(self.dir_prefix, "run_metadata.json")

    def get_data_map(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "name": ["run_name"],
            "s3_prefix": self.get_s3_url(self.dir_prefix),
            "https_prefix": self.get_https_url(self.dir_prefix),
        }

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return ["dataset_id", "name"]

    @classmethod
    def get_db_model_class(cls) -> type[Base]:
        return Run

    @classmethod
    def get_item(cls, dataset_id: int, dataset: DatasetDBImporter, config: DBImportConfig) -> "Iterator[RunDBImporter]":
        return [
            cls(dataset_id, run_prefix, dataset, config)
            for run_prefix in config.find_subdirs_with_files(dataset.dir_prefix, "run_metadata.json")
        ]


class StaleRunDeletionDBImporter(StaleParentDeletionDBImporter):
    ref_klass = RunDBImporter

    def get_filters(self) -> dict[str, Any]:
        return {"dataset_id": self.parent_id}

    def children_tables_references(self) -> dict[str, type[StaleDeletionDBImporter]]:
        from db_import.importers.tiltseries import StaleTiltSeriesDeletionDBImporter
        from db_import.importers.voxel_spacing import StaleVoxelSpacingDeletionDBImporter

        return {
            "tomogram_voxel_spacings": StaleVoxelSpacingDeletionDBImporter,
            "tiltseries": StaleTiltSeriesDeletionDBImporter,
        }
