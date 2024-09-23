from typing import Any

from common.finders import DefaultImporterFactory
from common.metadata import DepositionMetadata
from importers.base_importer import BaseImporter
from importers.deposition_key_photo import DepositionKeyPhotoImporter


class DepositionImporter(BaseImporter):
    type_key = "deposition"
    plural_key = "depositions"
    finder_factory = DefaultImporterFactory
    has_metadata = True
    dir_path = "depositions_metadata/{deposition_name}"
    metadata_path = "depositions_metadata/{deposition_name}/deposition_metadata.json"

    def import_item(self) -> None:
        pass

    def import_metadata(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return
        meta = DepositionMetadata(self.config.fs, self.name, self.get_base_metadata())
        extra_data = self.load_extra_metadata()
        if not self.get_base_metadata():
            print("Skipping the deposition metadata file write as there is no metadata to write.")
            return
        meta.write_metadata(self.get_metadata_path(), extra_data)

    def load_extra_metadata(self) -> dict[str, Any]:
        key_photo_importer = DepositionKeyPhotoImporter(
            self.config,
            metadata={},
            name=None,
            path=None,
            parents={"deposition": self},
        )
        return {
            "key_photos": key_photo_importer.get_metadata(),
        }
