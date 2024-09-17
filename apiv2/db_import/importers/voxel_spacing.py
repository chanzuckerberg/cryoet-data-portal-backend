import os
from typing import Any, Iterator

from database import models
from db_import.importers.base_importer import (
    BaseDBImporter,
    DBImportConfig,
    StaleDeletionDBImporter,
    StaleParentDeletionDBImporter,
)
from db_import.importers.run import RunDBImporter


class TomogramVoxelSpacingDBImporter(BaseDBImporter):
    def __init__(self, run_id: int, dir_prefix: str, parent: RunDBImporter, config: DBImportConfig):
        self.run_id = run_id
        self.dir_prefix = dir_prefix
        self.parent = parent
        self.config = config
        self.metadata = {}

    def get_data_map(self) -> dict[str, Any]:
        return {
            "voxel_spacing": float(os.path.basename(self.dir_prefix.strip("/"))[len("VoxelSpacing") :]),
            "s3_prefix": self.join_path(self.config.s3_prefix, self.dir_prefix),
            "https_prefix": self.join_path(self.config.https_prefix, self.dir_prefix),
            "run_id": self.run_id,
        }

    @classmethod
    def get_id_fields(cls) -> list[str]:
        return ["run_id", "voxel_spacing"]

    @classmethod
    def get_db_model_class(cls) -> type:
        return models.TomogramVoxelSpacing

    @classmethod
    def get_items(
        cls,
        run_id: int,
        run: RunDBImporter,
        config: DBImportConfig,
    ) -> "Iterator[TomogramVoxelSpacingDBImporter]":
        tomogram_path = cls.join_path(run.dir_prefix, "Tomograms/")
        return [
            cls(run_id, voxel_spacing_path, run, config)
            for voxel_spacing_path in config.glob_s3(tomogram_path, "VoxelSpacing*", is_file=False)
        ]


class StaleVoxelSpacingDeletionDBImporter(StaleParentDeletionDBImporter):
    ref_klass = TomogramVoxelSpacingDBImporter

    def get_filters(self) -> dict[str, Any]:
        return {"run_id": self.parent_id}

    def children_tables_references(self) -> dict[str, type[StaleDeletionDBImporter]]:
        from db_import.importers.annotation import StaleAnnotationDeletionDBImporter
        from db_import.importers.tomogram import StaleTomogramDeletionDBImporter

        return {
            "tomograms": StaleTomogramDeletionDBImporter,
            "annotations": StaleAnnotationDeletionDBImporter,
        }
