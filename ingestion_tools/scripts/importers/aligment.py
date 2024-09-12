from common.finders import DefaultImporterFactory
from importers.base_importer import BaseFileImporter


class AlignmentImporter(BaseFileImporter):
    type_key = "alignment"
    plural_key = "alignments"
    finder_factory = DefaultImporterFactory
    has_metadata = True

    # TODO: check if this is needed?
    # def import_metadata(self):
    #     dest_ts_metadata = self.get_metadata_path()
    #     base_metadata = self.get_base_metadata()
    #     metadata = AlignmentMetadata(self.config.fs, self.get_deposition().name, base_metadata)
    #     metadata.write_metadata(dest_ts_metadata, {})
