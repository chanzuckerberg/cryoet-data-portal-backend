import os
from typing import Optional

from common.finders import DefaultImporterFactory
from importers.base_importer import BaseKeyPhotoImporter
from importers.key_image import KeyImageImporter
from importers.run import RunImporter
from importers.tomogram import TomogramImporter
from importers.voxel_spacing import VoxelSpacingImporter


class DatasetKeyPhotoImporter(BaseKeyPhotoImporter):
    type_key = "dataset_keyphoto"
    plural_key = "dataset_keyphotos"
    finder_factory = DefaultImporterFactory
    has_metadata = False
    dir_path = "{dataset_name}/Images"

    def get_image_src_path(self) -> str:
        image_src = self.path or self.get_first_valid_tomo_key_photo(self.name)
        if not image_src:
            raise RuntimeError("Image source file not found")
        return image_src

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

    @classmethod
    def get_default_config(cls) -> list[dict] | None:
        return [{"sources": [{"literal": {"value": ["snapshot", "thumbnail"]}}]}]
