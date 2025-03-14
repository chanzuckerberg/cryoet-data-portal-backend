from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter


class RawTiltImporter(BaseFileImporter):
    type_key = "rawtilt"
    plural_key = "rawtilts"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = "{dataset_name}/{run_name}/TiltSeries/{tiltseries_id}"
