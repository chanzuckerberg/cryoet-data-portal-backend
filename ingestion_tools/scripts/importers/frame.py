from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter


class FrameImporter(BaseFileImporter):
    type_key = "frame"
    plural_key = "frames"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = "{dataset_name}/{run_name}/Frames"
