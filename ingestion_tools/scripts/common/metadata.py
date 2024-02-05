import os
import re
from typing import Any, Dict

from common.formats import tojson
from common.fs import FileSystemApi
from common.merge import deep_merge


class BaseMetadata:
    def __init__(self, fs: FileSystemApi, template: dict[str, Any]):
        self.fs = fs
        self.metadata = template

    def write_metadata(self, filename: str, is_json=True) -> None:
        with self.fs.open(filename, "w") as fh:
            data = tojson(self.metadata) if is_json else self.metadata
            fh.write(data)


class MergedMetadata(BaseMetadata):
    def write_metadata(self, filename: str, merge_data: dict[str, Any]) -> None:
        metadata = deep_merge(self.metadata, merge_data)
        with self.fs.open(filename, "w") as fh:
            fh.write(tojson(metadata))


class TiltSeriesMetadata(MergedMetadata):
    pass


class DatasetMetadata(MergedMetadata):
    pass


class RunMetadata(MergedMetadata):
    pass


class TomoMetadata(MergedMetadata):
    pass


class NeuroglancerMetadata(BaseMetadata):
    pass


class AnnotationMetadata(MergedMetadata):
    def get_filename_prefix(self, output_dir: str, identifier: int) -> str:
        version = self.metadata["version"]
        obj = None
        try:
            obj = self.metadata["annotation_object"]["description"]
        except KeyError:
            pass
        if not obj:
            obj = self.metadata["annotation_object"]["name"]
        dest_filename = os.path.join(
            output_dir,
            "-".join(
                [
                    str(identifier),
                    re.sub("[^0-9a-z]", "_", obj.lower()),
                    re.sub("[^0-9a-z.]", "_", f"{version.lower()}"),
                ]
            ),
        )
        return dest_filename
