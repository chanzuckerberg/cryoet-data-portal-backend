from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter


class CollectionMetadataImporter(BaseFileImporter):
    type_key = plural_key = "collection_metadata"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = "{dataset_name}/{run_name}/Frames"
