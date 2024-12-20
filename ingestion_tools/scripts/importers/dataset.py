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
        meta = DatasetMetadata(self.config.fs, self.get_deposition().name, self.get_base_metadata())
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
