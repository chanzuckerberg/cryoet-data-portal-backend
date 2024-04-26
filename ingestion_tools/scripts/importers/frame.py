from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter


class FrameImporterFactory(DefaultImporterFactory):
    pass


class FrameImporter(BaseFileImporter):
    type_key = "frames"
    finder_factory = DefaultImporterFactory
    dependencies = ["run"]
    has_metadata = False