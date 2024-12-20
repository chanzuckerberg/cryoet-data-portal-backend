import os
from typing import Generator

import imageio
import numpy as np
from PIL import Image

from common.finders import DefaultImporterFactory
from common.image import ZarrReader
from common.make_key_image import KeyMaskAnnotation, KeyPointAnnotation, generate_preview, process_key_image
from importers.annotation import AnnotationImporter
from importers.base_importer import BaseImporter
from importers.visualization_config import VisualizationConfigImporter


class KeyImageImporter(BaseImporter):
    type_key = "key_image"
    plural_key = "key_images"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    width_sizes = {
        "original": "orig",  # uncropped, may be used to display to user later on
        "thumbnail": 134,  # small thumbnail
        "snapshot": 512,  # small detail expand
        "expanded": 1024,  # large detail expand
    }
    dir_path = "{dataset_name}/{run_name}/Reconstructions/VoxelSpacing{voxel_spacing_name}/Images/{tomogram_id}/"

    def get_metadata(self) -> dict[str, str]:
        return {
            "snapshot": self.find_key_image_path("snapshot"),
            "thumbnail": self.find_key_image_path("thumbnail"),
        }

    def find_key_image_path(self, image_type: str) -> str:
        image_path = os.path.join(self.get_output_path(), self.get_file_name(image_type))
        return os.path.relpath(image_path, self.config.output_prefix)

    def import_item(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return
        dir = self.get_output_path()
        preview, tomo_width = None, None
        if self.path:
            preview, tomo_width = self.get_existing_preview()
        if preview is None:
            preview, tomo_width = self.generate_preview_from_tomo()

        width = self.width_sizes[self.name]
        if width == "orig":
            # resize matplotlib render to original tomogram dimensions
            image = process_key_image(preview, aspect_ratio=None, width=tomo_width, rotate=False)
        else:
            image = process_key_image(preview, aspect_ratio="4:3", width=width, rotate=True)
        filename = self.config.fs.localwritable(os.path.join(dir, self.get_file_name(self.name)))

        imageio.imsave(filename, image)
        print(f"key photo saved at {filename}")
        self.config.fs.push(filename)

    def get_existing_preview(self) -> tuple[np.ndarray | None, int | None]:
        config = self.config
        run = self.get_run()
        for fname in config.glob_files(run, self.path):
            file_name = config.fs.localreadable(fname)
            img = Image.open(file_name)
            img.load()
            data = np.asarray(img, dtype="int32")
            return data, data.shape[-1]
        return None, None

    def load_point_annotations(self, annotation_colors: dict[str, str]) -> Generator[KeyPointAnnotation, None, None]:
        for annotation in AnnotationImporter.finder(self.config, **self.parents):
            is_default = annotation.is_visualization_default
            if annotation.shape.lower() in {"orientedpoint", "point"} and is_default:
                annotation_path = annotation.get_output_path()
                annotation_filename = annotation.get_output_filename(annotation_path)
                color = annotation_colors.get(self.config.to_formatted_path(annotation_filename))
                print(f"loading point annotation: {annotation_filename} color:{color}")
                try:
                    annotation_data = annotation.get_output_data(annotation_path)
                    yield KeyPointAnnotation(color=color, data=annotation_data)
                except FileNotFoundError:
                    print(f"Unable to load annotation data for {annotation_filename}")

    def load_mask_annotations(self, annotation_colors: dict[str, str]) -> Generator[KeyMaskAnnotation, None, None]:
        for annotation in AnnotationImporter.finder(self.config, **self.parents):
            is_default = annotation.is_visualization_default
            if annotation.shape.lower() == "segmentationmask" and is_default:
                annotation_path = annotation.get_output_filename(annotation.get_output_path(), "zarr")
                color = annotation_colors.get(self.config.to_formatted_path(annotation_path))
                print(f"loading mask annotation: {annotation_path} color:{color}")
                try:
                    annotation_data = ZarrReader(self.config.fs, annotation_path).get_data()
                    yield KeyMaskAnnotation(color=color, data=annotation_data)
                except FileNotFoundError:
                    print(f"Unable to load annotation data for {annotation_path}")

    def get_annotation_colors(self) -> dict[str, str]:
        """Get the color associated with the annotation from the visualization config."""
        viz_config_importer = VisualizationConfigImporter(self.config, {}, parents=self.parents)
        tomogram = self.get_tomogram()
        layer_info = viz_config_importer.get_annotation_layer_info(tomogram.alignment_metadata_path)
        return {key: val["args"]["color"] for key, val in layer_info.items()}

    def generate_preview_from_tomo(self) -> tuple[np.ndarray, np.ndarray]:
        tomo_filename = self.get_tomogram().get_output_path() + ".zarr"

        # TODO: optimize to check if image needs to be regenerated
        print(f"loading tomogram {tomo_filename}")
        data = ZarrReader(self.config.fs, tomo_filename).get_data()
        annotation_colors = self.get_annotation_colors()
        preview = generate_preview(
            data,
            projection_depth=40,
            point_annotations=self.load_point_annotations(annotation_colors),
            mask_annotations=self.load_mask_annotations(annotation_colors),
        )
        return preview, data.shape[-1]

    @classmethod
    def get_file_name(cls, image_type: str) -> str:
        return f"key-photo-{image_type}.png"

    @classmethod
    def get_default_config(cls) -> list[dict] | None:
        return [{"sources": [{"literal": {"value": ["original", "snapshot", "thumbnail", "expanded"]}}]}]
