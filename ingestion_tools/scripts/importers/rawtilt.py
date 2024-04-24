from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter


class RawTiltImporter(BaseFileImporter):
    type_key = "rawtilt"
    finder_factory = DefaultImporterFactory
    dependencies = ["run"]
    has_metadata = False
