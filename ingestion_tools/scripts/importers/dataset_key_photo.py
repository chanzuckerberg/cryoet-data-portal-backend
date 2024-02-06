import os
from typing import TYPE_CHECKING, Optional

from common.config import DataImportConfig
from common.copy import copy_by_src
from importers.base_importer import BaseImporter
from importers.key_image import KeyImageImporter
from importers.run import RunImporter
from importers.tomogram import TomogramImporter

if TYPE_CHECKING:
    from importers.dataset import DatasetImporter
else:
    DatasetImporter = "DatasetImporter"


class DatasetKeyPhotoImporter(BaseImporter):
    type_key = "dataset_keyphoto"
    image_keys = ["snapshot", "thumbnail"]

    def import_key_photo(self):
        path = self.config.get_output_path(self)
        for image_type in ["snapshot", "thumbnail"]:
            self.save_image(image_type, path)

    def get_metadata(self) -> dict[str, str]:
        path = self.config.get_output_path(self)
        image_files = self.config.fs.glob(f"{path}/*")
        return {key: self.get_image_file(image_files, f"{path}/{key}") for key in self.image_keys}  # type: ignore

    def get_image_file(self, key_photo_files: list[str], prefix: str) -> str | None:
        image_path = next(filter(lambda file: file.startswith(prefix), key_photo_files), None)
        if image_path:
            return os.path.relpath(image_path, self.config.output_prefix)
        return None

    def save_image(self, key: str, path: str) -> Optional[str]:
        image_src = self.config.dataset_template.get("key_photos", {}).get(key) or self.get_first_valid_tomo_key_photo(
            key,
        )
        if not image_src:
            raise RuntimeError("Image source file not found")
        _, extension = os.path.splitext(image_src)
        dest_path = os.path.join(path, key) + extension
        copy_by_src(image_src, dest_path, self.config.fs)
        return os.path.relpath(dest_path, self.config.output_prefix)

    def get_first_valid_tomo_key_photo(self, key: str) -> Optional[str]:
        for run in RunImporter.find_runs(self.config, self.get_dataset()):
            for tomo in TomogramImporter.find_tomograms(self.config, run):
                key_photos = KeyImageImporter(self.config, parent=tomo).get_metadata()
                if all(image_key in key_photos for image_key in self.image_keys):
                    return os.path.join(self.config.output_prefix, key_photos.get(key))
        return None

    @classmethod
    def find_dataset_key_photos(cls, config: DataImportConfig, dataset: "DatasetImporter") -> "DatasetKeyPhotoImporter":
        return cls(config=config, parent=dataset)
