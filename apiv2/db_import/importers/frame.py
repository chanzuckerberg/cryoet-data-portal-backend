import os
from typing import Any

from database import models
from db_import.common.finders import FileFinder
from db_import.importers.base import IntegratedDBImporter, ItemDBImporter

# Frame Fields
#   deposition_id: int
#   run_id: int
#   raw_angle: int
#   acquisition_order: int
#   dose: float
#   is_gain_corrected: bool
#   s3_frame_path: str
#   https_frame_path: str


class FrameItem(ItemDBImporter):
    direct_mapped_fields = {}
    id_fields = ["run_id", "s3_frame_path"]
    model_class = models.Frame

    def load_computed_fields(self):
        https_prefix = self.config.https_prefix
        s3_prefix = self.config.s3_prefix

        self.model_args["s3_frame_path"] = os.path.join(s3_prefix, self.input_data["file"])
        self.model_args["https_frame_path"] = os.path.join(https_prefix, self.input_data["file"])
        self.model_args["run_id"] = self.input_data["run"].id
        self.model_args["deposition_id"] = self.input_data["deposition"].id


class FrameImporter(IntegratedDBImporter):
    finder = FileFinder
    row_importer = FrameItem
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
            "path": os.path.join(self.run.s3_prefix, "Frames/"),
            "glob": "*",
            "match_regex": r"^(?:(?!_gain\.).)*(?<!mdoc)$",
        }
