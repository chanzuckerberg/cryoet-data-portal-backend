import os
from typing import Any

from database import models
from db_import.common.finders import MetadataFileFinder
from db_import.importers.base import IntegratedDBImporter, ItemDBImporter


class IdentifiedObjectItem(ItemDBImporter):
    id_fields = ["run_id", "object_id", "object_name", "object_state", "object_description"]
    model_class = models.IdentifiedObject
    direct_mapped_fields = {
        "object_id": ["id"],
        "object_name": ["name"],
        "object_state": ["state"],
        "object_description": ["description"],
    }

    def load_computed_fields(self):
        extra_data = {"run_id": self.input_data["run"].id}
        self.model_args.update(extra_data)

class IdentifiedObjectImporter(IntegratedDBImporter):
    finder = MetadataFileFinder
    row_importer = IdentifiedObjectItem
    clean_up_siblings = True

    def __init__(self, config, run: models.Run, **unused_parents):
        self.run = run
        self.config = config
        self.parents = {"run": run}

    def get_filters(self) -> dict[str, Any]:
        return {"run_id": self.run.id}

    def get_finder_args(self) -> dict[str, Any]:
        return {
            "path": os.path.join(self.run.s3_prefix, "IdentifiedObjects/"),
            "file_glob": "*.csv",
        }
