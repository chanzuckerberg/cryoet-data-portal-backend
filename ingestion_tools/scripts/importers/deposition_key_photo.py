from common.finders import DefaultImporterFactory
from importers.base_importer import BaseKeyPhotoImporter


class DepositionKeyPhotoImporter(BaseKeyPhotoImporter):
    type_key = "deposition_keyphoto"
    plural_key = "deposition_keyphotos"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = "depositions_metadata/{deposition_name}/Images"

    def get_image_src_path(self) -> str | None:
        return self.path
