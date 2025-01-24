import contextlib
import os
import re
from copy import deepcopy
from datetime import datetime
from typing import Any

from common.formats import tojson
from common.fs import FileSystemApi
from common.merge import deep_merge


class BaseMetadata:
    def __init__(self, fs: FileSystemApi, deposition_id: str, template: dict[str, Any]):
        self.fs = fs
        self.metadata = template
        self.deposition_id = deposition_id

    def add_defaults(self, metadata: dict[str, Any]) -> dict[str, Any]:
        if not metadata.get("deposition_id"):
            metadata["deposition_id"] = self.deposition_id
        metadata["last_updated_at"] = int(datetime.now().timestamp())
        return metadata

    def write_metadata(self, filename: str, is_json=True) -> None:
        metadata = deepcopy(self.metadata)
        metadata = self.add_defaults(metadata)
        with self.fs.open(filename, "w") as fh:
            data = tojson(metadata) if is_json else self.metadata
            fh.write(data)


class MergedMetadata(BaseMetadata):
    def write_metadata(self, filename: str, merge_data: dict[str, Any]) -> None:
        metadata = deep_merge(self.metadata, merge_data)
        metadata = self.add_defaults(metadata)
        kwargs = {"ContentType": "application/json"}
        with self.fs.open(filename, "w", **kwargs) as fh:
            fh.write(tojson(metadata))


class TiltSeriesMetadata(MergedMetadata):
    pass


class AlignmentMetadata(MergedMetadata):
    pass


class DatasetMetadata(MergedMetadata):
    pass


class DepositionMetadata(MergedMetadata):
    pass


class RunMetadata(MergedMetadata):
    pass


class TomoMetadata(MergedMetadata):
    pass


class NeuroglancerMetadata(BaseMetadata):
    pass


class AnnotationMetadata(MergedMetadata):
    def get_filename_prefix(self, output_dir: str) -> str:
        version = self.metadata["version"]
        obj = None
        with contextlib.suppress(KeyError):
            obj = self.metadata["annotation_object"]["description"]
        if not obj:
            obj = self.metadata["annotation_object"]["name"]
        dest_filename = os.path.join(
            output_dir,
            "-".join(
                [
                    re.sub("[^0-9a-z]", "_", obj.lower()),
                    re.sub("[^0-9a-z.]", "_", f"{str(version).lower()}"),
                ],
            ),
        )
        return dest_filename
