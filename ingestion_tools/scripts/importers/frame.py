from importers.base_importer import BaseFileImporter
from common.finders import DefaultImporterFactory

class FrameImporterFactory(DefaultImporterFactory):
    pass


class FrameImporter(BaseFileImporter):
    type_key = "frames"
    finder_factory = DefaultImporterFactory
    dependencies = ["run"]
    has_metadata = False