from typing import TYPE_CHECKING

from importers.base_importer import BaseImporter

from common.config import DataImportConfig
from common.metadata import VoxelSpacingMetadata

if TYPE_CHECKING:
    from importers.run import RunImporter
else:
    RunImporter = "RunImporter"


class VoxelSpacingImporter(BaseImporter):
    type_key = "alignment"

    def write_index_file(self):
        # TODO FIXME we should write an index file that lists all the voxel spacings we have for a given run so that nobody has to list dirs!!
        pass

    @classmethod
    def find(
        cls,
        config: DataImportConfig,
        run: RunImporter,
        skip_cache: bool = False,
    ) -> list["AlignmentImporter"]:
        return [cls(config=config, parent=run, path="TODO")]

    def import_metadata(self, output_prefix: str) -> None:
        meta = VoxelSpacingMetadata(self.config.fs, self.config.deposition_id, self.config.alignment_template)
        extra_data = {"deposition_identifier": 12445}  # TODO FIXME
        meta.write_metadata(self.get_metadata_path(), extra_data)
