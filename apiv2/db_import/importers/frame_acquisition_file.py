import os
from typing import Any

from database import models
from db_import.common.finders import MetadataFileFinder
from db_import.importers.base import IntegratedDBImporter, ItemDBImporter

# FrameAcquisitionFile Fields
#   run_id: int
#   s3_mdoc_path: str
#   https_mdoc_path: str


class FrameAcquisitionFileItem(ItemDBImporter):
    direct_mapped_fields = {}
    id_fields = ["run_id", "s3_mdoc_path"]
    model_class = models.FrameAcquisitionFile

    def load_computed_fields(self):
        file = self.input_data["frames_acquisition_file"]
        self.model_args["s3_mdoc_path"] = self.get_s3_url(file)
        self.model_args["https_mdoc_path"] = self.get_https_url(file)
        self.model_args["run_id"] = self.input_data["run"].id


class FrameAcquisitionFileImporter(IntegratedDBImporter):
    finder = MetadataFileFinder
    row_importer = FrameAcquisitionFileItem
    clean_up_siblings = True

    def __init__(self, config, run: models.Run, **unused_parents):
        self.run = run
        self.config = config
        self.parents = {"run": run}

    def get_filters(self) -> dict[str, Any]:
        return {"run_id": self.run.id}

    def get_finder_args(self) -> dict[str, Any]:
        return {
            "path": os.path.join(self.run.s3_prefix, "Frames/"),
            "file_glob": "frames_metadata.json",
        }
