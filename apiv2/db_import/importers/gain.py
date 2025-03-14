import os
from typing import Any

from database import models

from db_import.common.finders import FileFinder
from db_import.importers.base import IntegratedDBImporter, ItemDBImporter

# GainFile Fields
#   run_id: int
#   s3_file_path: str
#   https_file_path: str


class GainItem(ItemDBImporter):
    direct_mapped_fields = {}
    id_fields = ["run_id", "s3_file_path"]
    model_class = models.GainFile

    def load_computed_fields(self):
        self.model_args["run_id"] = self.input_data["run"].id
        self.model_args["s3_file_path"] = self.get_s3_url(self.input_data["file"])
        self.model_args["https_file_path"] = self.get_https_url(self.input_data["file"])


class GainImporter(IntegratedDBImporter):
    finder = FileFinder
    row_importer = GainItem
    clean_up_siblings = True

    def __init__(self, config, run: models.Run, dataset: models.Dataset, **unused_parents):
        self.run = run
        self.dataset = dataset
        self.deposition = dataset.deposition  # for now frames can only be deposited with a dataset.
        self.config = config
        self.parents = {"run": run, "dataset": dataset, "deposition": self.deposition}

    def get_filters(self) -> dict[str, Any]:
        return {"run_id": self.run.id}

    def get_finder_args(self) -> dict[str, Any]:
        return {
            "path": os.path.join(self.run.s3_prefix, "Gains/"),
            "glob": "*_gain*",
            "match_regex": ".*",
        }
