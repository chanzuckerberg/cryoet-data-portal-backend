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

    def import_item(self) -> None:
        pass

    def import_metadata(self) -> None:
        meta = DepositionMetadata(self.config.fs, self.config.deposition_id, self.get_base_metadata())
        extra_data = self.load_extra_metadata()
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
