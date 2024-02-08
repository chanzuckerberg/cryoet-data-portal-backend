import os
from typing import TYPE_CHECKING, Generator

import imageio
import numpy as np
from PIL import Image

from common.config import DataImportConfig
from common.image import ZarrReader
from common.make_key_image import generate_preview, process_key_image
from importers.annotation import AnnotationImporter
from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.tomogram import TomogramImporter
else:
    TomogramImporter = "TomogramImporter"


class KeyImageImporter(BaseImporter):
    type_key = "key_image"
    width_sizes = {
        "original": "orig",  # uncropped, may be used to display to user later on
        "thumbnail": 134,  # small thumbnail
        "snapshot": 512,  # small detail expand
        "expanded": 1024,  # large detail expand
    }

    @classmethod
    def find_key_images(cls, config: DataImportConfig, tomogram: TomogramImporter) -> "KeyImageImporter":
        return [cls(config, parent=tomogram)]

    def get_metadata(self) -> dict[str, str]:
        return {
            "snapshot": self.find_key_image_path("snapshot"),
            "thumbnail": self.find_key_image_path("thumbnail"),
        }

    def find_key_image_path(self, image_type: str) -> str:
        image_path = os.path.join(self.get_output_path(), self.get_file_name(image_type))
        return os.path.relpath(image_path, self.config.output_prefix)

    def make_key_image(self, config: DataImportConfig, upload: bool = True) -> None:
        dir = self.get_output_path()
        preview, tomo_width = None, None
        if config.tomo_key_photo_glob:
            preview, tomo_width = self.get_existing_preview()
        if preview is None:
            preview, tomo_width = self.generate_preview_from_tomo()

        for image_type, width in self.width_sizes.items():
            if width == "orig":
                # resize matplotlib render to original tomogram dimensions
                image = process_key_image(preview, aspect_ratio=None, width=tomo_width, rotate=False)
            else:
                image = process_key_image(preview, aspect_ratio="4:3", width=width, rotate=True)
            filename = self.config.fs.localwritable(os.path.join(dir, self.get_file_name(image_type)))

            imageio.imsave(filename, image)
            print(f"key photo saved at {filename}")

            if upload:
                self.config.fs.push(filename)

    def get_existing_preview(self) -> tuple[np.ndarray | None, int | None]:
        config = self.config
        run = self.get_run()
        for fname in config.glob_files(run, config.tomo_key_photo_glob):
            file_name = config.fs.localreadable(fname)
            img = Image.open(file_name)
            img.load()
            data = np.asarray(img, dtype="int32")
            return data, data.shape[-1]
        return None, None

    def generate_preview_from_tomo(self) -> tuple[np.ndarray, np.ndarray]:
        tomo_filename = self.parent.get_output_path() + ".zarr"

        # TODO: optimize to check if image needs to be regenerated
        print(f"loading tomogram {tomo_filename}")
        data = ZarrReader(self.config.fs, tomo_filename).get_data()

        def load_annotations() -> Generator[np.ndarray, None, None]:
            for annotation in AnnotationImporter.find_annotations(self.config, self.parent):
                for source in annotation.sources:
                    if source.shape.lower() not in ["orientedpoint", "point"]:
                        continue
                    # yield our point data
                    yield source.get_output_data(self.config.fs, annotation.get_output_path())
                    # We prefer point files over oriented point files, so stop if we just processed that.
                    if source.shape.lower() == "point":
                        break

        preview = generate_preview(data, projection_depth=40, annotations=load_annotations(), cmap="tab10")
        return preview, data.shape[-1]

    @staticmethod
    def get_file_name(image_type: str) -> str:
        return f"key-photo-{image_type}.png"
