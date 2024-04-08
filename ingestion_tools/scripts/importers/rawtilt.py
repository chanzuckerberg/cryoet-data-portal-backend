from importers.base_importer import BaseFileImporter
from common.finders import DefaultImporterFactory

class RawTiltImporter(BaseFileImporter):
    type_key = "rawtilt"
    finder_factory = DefaultImporterFactory
    dependencies = ["run"]
    has_metadata = False