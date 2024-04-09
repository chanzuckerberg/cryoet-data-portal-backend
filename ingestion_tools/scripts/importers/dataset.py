from common.metadata import DatasetMetadata
from importers.base_importer import BaseImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter
from typing import Any


class DatasetImporter(BaseImporter):
    type_key = "dataset"

    def __init__(
        self,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ):
        super().__init__(*args, **kwargs)

    def import_metadata(self, output_prefix: str) -> None:
        meta = DatasetMetadata(self.config.fs, self.config.deposition_id, self.config.dataset_template)
        extra_data = self.load_extra_metadata()
        meta.write_metadata(self.get_metadata_path(), extra_data)

    def load_extra_metadata(self) -> dict[str, dict[str, str]]:
        key_photo_importer = DatasetKeyPhotoImporter.find_dataset_key_photos(self.config, self)

        return {
            "key_photos": key_photo_importer.get_metadata(),
        }
