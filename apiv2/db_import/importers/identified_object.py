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

        if "run" in self.input_data and hasattr(self.input_data["run"], "id"):
            extra_data = {"run_id": self.input_data["run"].id}
            self.model_args.update(extra_data)
        else:
            run_identifier = self.input_data.get("run_identifier")
            if run_identifier:
                try:
                    run_query = sa.select(models.Run).where(models.Run.name == run_identifier)
                    run = self.config.session.scalars(run_query).one()
                    self.model_args["run_id"] = run.id
                except Exception as e:
                    raise ValueError(f"Could not find run with identifier '{run_identifier}': {e}") from e
            else:
                raise ValueError("No run object or run_identifier provided")

    def load(self, session):
        return super().load(session)


class IdentifiedObjectImporter(IntegratedDBImporter):
    finder = JsonDataFinder
    row_importer = IdentifiedObjectItem
    clean_up_siblings = True

    def __init__(self, config, run, run_id: int = None, **unused_parents):
        self.run = run
        self.run_id = run_id
        self.config = config
        self.parents = {"run": run}

    def get_filters(self) -> dict[str, Any]:
        if self.run_id:
            return {"run_id": self.run_id}
        else:
            return {"run_id": self.run.id}

    def get_finder_args(self) -> dict[str, Any]:

        if hasattr(self.run, "s3_prefix"):
            s3_prefix = self.run.s3_prefix
        elif hasattr(self.run, "dir_prefix"):
            s3_prefix = self.run.get_s3_url(self.run.dir_prefix)
        else:
            raise AttributeError(f"Run object {type(self.run)} has neither s3_prefix nor dir_prefix")

        if s3_prefix.startswith("s3://"):
            parts = s3_prefix.split("/", 3)
            if len(parts) >= 4:
                s3_prefix = parts[3]

        path = f"{self.config.bucket_name}/{s3_prefix.rstrip('/')}/IdentifiedObjects/identified_objects.json"

        run_identifier = self.run.metadata.get("run_name")

        return {
            "path": path,
            "match_key": "run_identifier",
            "match_value": run_identifier,
        }
