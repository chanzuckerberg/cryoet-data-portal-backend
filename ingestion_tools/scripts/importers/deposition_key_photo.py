import os

from common.copy import copy_by_src
from common.finders import DefaultImporterFactory
from importers.base_importer import BaseImporter


class DepositionKeyPhotoImporter(BaseImporter):
    type_key = "deposition_keyphoto"
    plural_key = "deposition_keyphotos"
    image_keys = ["snapshot", "thumbnail"]
    finder_factory = DefaultImporterFactory
    has_metadata = False

    def import_item(self) -> None:
        path = self.config.get_output_path(self)
        self.save_image(self.name, path)

    def save_image(self, key: str, path: str) -> None:
        image_src = self.path
        if not image_src:
            return None
        _, extension = os.path.splitext(image_src)
        dest_path = os.path.join(path, key) + extension
        copy_by_src(image_src, dest_path, self.config.fs)

    def get_metadata(self) -> dict[str, str]:
        path = self.config.get_output_path(self)
        image_files = self.config.fs.glob(f"{path}/*")
        return {key: self.get_image_file(image_files, f"{path}/{key}") for key in self.image_keys}

    def get_image_file(self, key_photo_files: list[str], prefix: str) -> str | None:
        image_path = next(filter(lambda file: file.startswith(prefix), key_photo_files), None)
        if image_path:
            return os.path.relpath(image_path, self.config.output_prefix)
        return None
