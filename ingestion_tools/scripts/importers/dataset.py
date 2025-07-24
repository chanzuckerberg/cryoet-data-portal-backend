from copy import deepcopy
from typing import Any

from common.finders import DefaultImporterFactory
from common.metadata import DatasetMetadata
from importers.base_importer import BaseImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter


class DatasetImporter(BaseImporter):
    type_key = "dataset"
    plural_key = "datasets"
    finder_factory = DefaultImporterFactory
    has_metadata = True
    dir_path = "{dataset_name}"
    metadata_path = "{dataset_name}/dataset_metadata.json"

    def import_item(self) -> None:
        pass

    def import_metadata(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name} metadata")
            return
        formatted_base_data = self.format_data(deepcopy(self.get_base_metadata()))
        meta = DatasetMetadata(self.config.fs, self.get_deposition().name, formatted_base_data)
        extra_data = self.load_extra_metadata()
        meta.write_metadata(self.get_metadata_path(), extra_data)

    # TODO fixme we should see what's best here.
    def load_extra_metadata(self) -> dict[str, dict[str, str]]:
        key_photo_importer = DatasetKeyPhotoImporter(
            self.config,
            metadata={},
            name=None,
            path=None,
            parents={"dataset": self},
        )

        return {
            "key_photos": key_photo_importer.get_metadata(),
        }

    @classmethod
    def format_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Format the dataset metadata to ensure all required fields are present.
        """
        keys = [
            "assay",
            "cell_component",
            "cell_strain",
            "cell_type",
            "development_stage",
            "disease",
            "organism",
            "tissue",
        ]
        for key in keys:
            if key not in data:
                data[key] = {}
            if not data[key].get("name"):
                data[key]["name"] = "not_reported"
            if key == "organism":
                if not data[key].get("taxonomy_id"):
                    data[key]["taxonomy_id"] = None
            elif not data[key].get("id"):
                data[key]["id"] = "not_reported"

        return data
