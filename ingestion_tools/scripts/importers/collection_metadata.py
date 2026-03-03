import os

from mdocfile.data_models import Mdoc

from common.config import DepositionImportConfig
from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter


class CollectionMetadataImporter(BaseFileImporter):
    type_key = plural_key = "collection_metadata"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = "{dataset_name}/{run_name}/Frames"

    def get_destination_path(self) -> str:
        filename = f"{self.parents['run'].name}.mdoc"
        return os.path.join(self.get_output_path(), filename)

    def get_output_data(self) -> Mdoc:
        path = self.get_destination_path()
        local_path = self.config.fs.localreadable(path)
        return Mdoc.from_file(local_path)

    @classmethod
    def get_importer(cls, config: DepositionImportConfig, **parents) -> "CollectionMetadataImporter":
        importers = list(cls.finder(config, **parents))
        if importers:
            return importers[-1]
        raise FileNotFoundError(f"No mdoc found for run: {parents['run'].name}")
