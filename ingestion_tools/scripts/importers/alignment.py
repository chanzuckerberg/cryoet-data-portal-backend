from typing import TYPE_CHECKING

from importers.base_importer import BaseImporter

from common.config import DataImportConfig
from common.metadata import AlignmentMetadata

if TYPE_CHECKING:
    from importers.voxel_spacing import VoxelSpacingImporter
else:
    VoxelSpacingImporter = "VoxelSpacingImporter"


class AlignmentImporter(BaseImporter):
    type_key = "alignment"

    def write_index_file():
        # TODO FIXME we should write an index file that lists all the alignments we have for a given run so that nobody has to list dirs!!
        pass

    @classmethod
    def find(
        cls,
        config: DataImportConfig,
        voxel_spacing: VoxelSpacingImporter,
        skip_cache: bool = False,
    ) -> list["AlignmentImporter"]:
        return [cls(config=config, parent=voxel_spacing, path="TODO")]

    def import_metadata(self, output_prefix: str) -> None:
        meta = AlignmentMetadata(self.config.fs, self.config.deposition_id, self.config.alignment_template)
        extra_data = {"deposition_identifier": 12445}  # TODO FIXME
        meta.write_metadata(self.get_metadata_path(), extra_data)
