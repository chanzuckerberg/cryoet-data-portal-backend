
import json
from typing import Any

import pandas as pd

from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from common.id_helper import IdentifierHelper
from common.metadata import IdentifiedObjectMetadata
from importers.base_importer import BaseFileImporter


class IdentifiedObjectIdentifierHelper(IdentifierHelper):
    @classmethod
    def _get_container_key(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        return "-".join([parents["run"].get_output_path(), "identified_object"])

    @classmethod
    def _get_metadata_glob(cls, config, parents, *args, **kwargs) -> str:
        run = parents["run"]
        metadata_glob = config.resolve_output_path("identified_object_metadata", run)
        return metadata_glob

    @classmethod
    def _generate_hash_key(
        cls,
        container_key: str,
        metadata: dict[str, Any],
        parents: dict[str, Any],
        *args,
        **kwargs,
    ) -> str:
        return "-".join(
            [
                container_key,
                str(metadata.get("deposition_id", int(parents["deposition"].name))),
                str(metadata.get("run_name", parents["run"].name)),
            ],
        )


class IdentifiedObjectImporter(BaseFileImporter):
    type_key = "identified_object"
    plural_key = "identified_objects"
    finder_factory = DefaultImporterFactory
    has_metadata = True
    dir_path = "{dataset_name}/{run_name}/IdentifiedObjects"
    metadata_path = "{dataset_name}/{run_name}/IdentifiedObjects/identified_objects_metadata.json"

    def __init__(
        self,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        allow_imports: bool,
        parents: dict[str, Any],
    ):
        super().__init__(
            config=config,
            metadata=metadata,
            name=name,
            path=path,
            allow_imports=allow_imports,
            parents=parents,
        )
        self.identifier = IdentifiedObjectIdentifierHelper.get_identifier(
            config, self.get_base_metadata(), self.parents,
        )

    def import_item(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return

        dest_path = self.get_output_path()
        try:
            with self.config.fs.open(self.path, "r") as f:
                df = pd.read_csv(f)
        except Exception as e:
            print(f"Error reading CSV {self.path}: {e}")
            return
        # Filter by run name and exclude run_name column
        run_name = self.parents["run"].name
        df_filtered = df[df['run_name'] == run_name].drop(columns=['run_name']) if 'run_name' in df.columns else df

        output_file = f"{dest_path}/identified_objects.json"
        with self.config.fs.open(output_file, "w") as f:
            df_filtered.to_json(f, orient='records', indent=4)

    def import_metadata(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name} metadata")
            return

        dest_path = self.get_output_path()
        json_file = f"{dest_path}/identified_objects.json"
        try:
            with self.config.fs.open(json_file, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON {json_file}: {e}")
            return

        extra_data = {
            "object_count": len(data),
            "columns": list(data[0].keys()) if data else [],
            "file_format": "json",
            "source_file": self.path,
            "identifier": self.path,
        }

        metadata = IdentifiedObjectMetadata(
            self.config.fs,
            self.get_deposition().name,
            self.get_base_metadata(),
        )

        metadata.write_metadata(self.get_metadata_path(), extra_data)
