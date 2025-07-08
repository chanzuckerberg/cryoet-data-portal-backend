from typing import Any

import sqlalchemy as sa

from database import models
from db_import.common.finders import JsonDataFinder
from db_import.importers.base import IntegratedDBImporter, ItemDBImporter


class IdentifiedObjectItem(ItemDBImporter):
    id_fields = ["run_id", "object_id", "object_name", "object_state", "object_description"]
    model_class = models.IdentifiedObject
    direct_mapped_fields = {
        "object_id": ["object_id"],
        "object_name": ["object_name"],
        "object_state": ["object_state"],
        "object_description": ["object_description"],
    }

    def load_computed_fields(self):
        run_identifier = self.input_data.get("run_identifier")
        if run_identifier:
            try:
                run_query = sa.select(models.Run).where(models.Run.name == run_identifier)
                run = self.config.session.scalars(run_query).one()
                self.model_args["run_id"] = run.id
            except Exception as e:
                raise ValueError(f"Could not find run with identifier '{run_identifier}': {e}")
        else:
            extra_data = {"run_id": self.input_data["run"].id}
            self.model_args.update(extra_data)
    
    def load(self, session):
        return super().load(session)

class IdentifiedObjectImporter(IntegratedDBImporter):
    finder = JsonDataFinder
    row_importer = IdentifiedObjectItem
    clean_up_siblings = True

    def __init__(self, config, run: models.Run, **unused_parents):
        self.run = run
        self.config = config
        self.parents = {"run": run}

    def get_filters(self) -> dict[str, Any]:
        return {"run_id": self.run.id}

    def get_finder_args(self) -> dict[str, Any]:
        s3_prefix = self.run.s3_prefix
        if s3_prefix.startswith("s3://"):
            parts = s3_prefix.split("/", 3)
            if len(parts) >= 4:
                s3_prefix = parts[3]
        
        path = f"{self.config.bucket_name}/{s3_prefix.rstrip('/')}/IdentifiedObjects/identified_objects.json"
        return {"path": path}

