from common.metadata import DatasetMetadata
from importers.base_importer import BaseImporter
from importers.dataset_key_photo import DatasetKeyPhotoImporter


class DatasetImporter(BaseImporter):
    type_key = "dataset"

    def import_metadata(self, output_prefix):
        meta = DatasetMetadata(self.config.fs, self.config.dataset_template)
        extra_data = self.load_extra_metadata()
        meta.write_metadata(self.get_metadata_path(), extra_data)

    def load_extra_metadata(self):
        key_photo_importer = DatasetKeyPhotoImporter.find_dataset_key_photos(self.config, self)
        return {
            "key_photos": key_photo_importer.get_metadata(),
        }
