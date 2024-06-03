from common.finders import DefaultImporterFactory
from importers.base_importer import BaseImporter


class VisualizationPrecomputeImporter(BaseImporter):
    type_key = "viz_precompute"
    plural_key = "viz_precompute"
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def import_item(self) -> None:
        annotation = self.get_annotation()
        annotation.neuroglancer_precompute(self.get_output_path())
