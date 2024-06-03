from common.finders import DefaultImporterFactory
from importers.base_importer import BaseImporter


class AnnotationVisualizationImporter(BaseImporter):
    type_key = "annotation_viz"
    plural_key = "annotations_viz"
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def import_item(self) -> None:
        precompute_path = self.get_output_path()
        annotation = self.get_annotation()
        annotation.neuroglancer_precompute(precompute_path)
