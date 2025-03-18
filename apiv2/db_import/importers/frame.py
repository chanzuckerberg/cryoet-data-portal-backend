import os
from typing import Any

from database import models
from db_import.common.finders import JsonDataFinder
from db_import.importers.base import IntegratedDBImporter, ItemDBImporter

# Frame Fields
#   deposition_id: int
#   run_id: int
#   acquisition_order: int
#   accumulated_dose: float
#   exposure_dose: float
#   is_gain_corrected: bool
#   s3_frame_path: str
#   https_frame_path: str
#   file_size: str


class FrameItem(ItemDBImporter):
    direct_mapped_fields = {}
    id_fields = ["run_id", "acquisition_order"]
    model_class = models.Frame

    def load_computed_fields(self):
        self.model_args["acquisition_order"] = self.input_data["acquisition_order"]
        self.model_args["accumulated_dose"] = self.input_data["accumulated_dose"]
        self.model_args["exposure_dose"] = self.input_data["exposure_dose"]
        self.model_args["is_gain_corrected"] = self.input_data["is_gain_corrected"]

        file_path = self.input_data["path"]
        self.model_args["s3_frame_path"] = self.get_s3_url(file_path) if file_path else None
        self.model_args["https_frame_path"] = self.get_https_url(file_path) if file_path else None
        self.model_args["file_size"] = self.get_file_size(self.input_data["file"]) if file_path else "0"

        self.model_args["run_id"] = self.input_data["run"].id
        self.model_args["deposition_id"] = self.input_data["deposition"].id


class FrameImporter(IntegratedDBImporter):
    finder = JsonDataFinder
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
            "path": os.path.join(self.run.s3_prefix, "Frames", "frames_metadata.json"),
            "list_key": ["frames"],
        }
