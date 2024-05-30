import os
from typing import TYPE_CHECKING, Optional

from common.copy import copy_by_src
from common.finders import DefaultImporterFactory
from importers.base_importer import BaseImporter
from importers.key_image import KeyImageImporter
from importers.run import RunImporter
from importers.tomogram import TomogramImporter
from importers.voxel_spacing import VoxelSpacingImporter

if TYPE_CHECKING:
    from importers.dataset import DatasetImporter
else:
    DatasetImporter = "DatasetImporter"


class DatasetKeyPhotoImporter(BaseImporter):
    type_key = "dataset_keyphoto"
    plural_key = "dataset_keyphotos"
    image_keys = ["snapshot", "thumbnail"]
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def import_item(self) -> None:
        path = self.config.get_output_path(self)
        self.save_image(self.name, path)

    def get_metadata(self) -> dict[str, str]:
        path = self.config.get_output_path(self)
        image_files = self.config.fs.glob(f"{path}/*")
        return {key: self.get_image_file(image_files, f"{path}/{key}") for key in self.image_keys}

    def get_image_file(self, key_photo_files: list[str], prefix: str) -> str | None:
        image_path = next(filter(lambda file: file.startswith(prefix), key_photo_files), None)
        if image_path:
            return os.path.relpath(image_path, self.config.output_prefix)
        return None

    def save_image(self, key: str, path: str) -> Optional[str]:
        image_src = self.path or self.get_first_valid_tomo_key_photo(key)
        if not image_src:
            raise RuntimeError("Image source file not found")
        _, extension = os.path.splitext(image_src)
        dest_path = os.path.join(path, key) + extension
        copy_by_src(image_src, dest_path, self.config.fs)
        return os.path.relpath(dest_path, self.config.output_prefix)

    def get_first_valid_tomo_key_photo(self, key: str) -> Optional[str]:
        for run in RunImporter.finder(self.config, **self.parents):
            for vs in VoxelSpacingImporter.finder(self.config, run=run, **self.parents):
                for tomo in TomogramImporter.finder(self.config, voxel_spacing=vs, run=run, **self.parents):
                    key_photos = list(
                        KeyImageImporter.finder(self.config, voxel_spacing=vs, run=run, tomogram=tomo, **self.parents),
                    )[0].get_metadata()
                    if all(image_key in key_photos for image_key in self.image_keys):
                        img_path = os.path.join(self.config.output_prefix, key_photos.get(key))
                        if self.config.fs.exists(img_path):
                            return img_path
        return None
