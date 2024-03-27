import contextlib
import json
import os
from typing import TYPE_CHECKING, Any

from importers.base_importer import BaseImporter

if TYPE_CHECKING:
    from importers.run import RunImporter
else:
    RunImporter = "RunImporter"


class VoxelSpacingImporter(BaseImporter):
    type_key = "voxel_spacing"

    def __init__(
        self,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ):
        super().__init__(*args, **kwargs)
        self.name = self.set_voxel_spacing(self.name)

    # TODO mutating importers is bad news :'(
    def set_voxel_spacing(self, voxel_spacing):
        self.name = self.format_voxel_spacing(float(voxel_spacing))

    @classmethod
    def format_voxel_spacing(cls, voxel_spacing: float) -> None:
        return "{:.3f}".format(round(voxel_spacing, 3))

    def get_voxel_spacing(self):
        return self.name

    def get_existing_annotation_metadatas(self, fs):
        # TODO use an annotation finder object here when we have one.
        metadata_glob = f"{self.config.resolve_output_path('annotation', self)}/*.json"
        metadatas = {}
        for file in fs.glob(metadata_glob):
            identifier = os.path.basename(file).split("-")[0]
            with contextlib.suppress(ValueError, TypeError):
                metadatas[int(identifier)] = json.loads(fs.open(file, "r").read())
        return metadatas
