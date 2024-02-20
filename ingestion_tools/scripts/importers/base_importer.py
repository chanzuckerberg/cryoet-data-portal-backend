import os
from typing import TYPE_CHECKING, Any, Optional

import numpy as np
from mrcfile.mrcobject import MrcObject

from common.image import get_header, get_tomo_metadata, get_voxel_size, scale_mrcfile

if TYPE_CHECKING:
    from common.config import DataImportConfig
    from importers.dataset import DatasetImporter
    from importers.run import RunImporter
    from importers.tomogram import TomogramImporter
else:
    RunImporter = "RunImporter"
    DatasetImporter = "DatasetImporter"
    TomogramImporter = "TomogramImporter"


class BaseImporter:
    type_key: str
    cached_find_results: dict[str, "BaseImporter"] = {}

    def __init__(self, config: "DataImportConfig", parent: Optional["BaseImporter"] = None):
        self.config = config
        self.parent = parent

    def parent_getter(self, type_key: str) -> "BaseImporter":
        parent = self
        while True:
            if not parent:
                raise ValueError(f"Could not find parent of type {type_key}")
            if parent.type_key == type_key:
                return parent
            else:
                parent = parent.parent

    def get_glob_vars(self) -> dict[str, Any]:
        run_name = self.get_run().run_name
        glob_vars = self.config.get_run_data_map(run_name)

        glob_vars["run_name"] = run_name
        # TODO: remove these in favor of the singular tsv file
        glob_vars["mapped_tomo_name"] = (self.config.run_to_tomo_map or {}).get(run_name)
        glob_vars["mapped_frame_name"] = (self.config.run_to_frame_map or {}).get(run_name)
        glob_vars["mapped_ts_name"] = (self.config.run_to_ts_map or {}).get(run_name)

        return glob_vars

    def get_run(self) -> RunImporter:
        return self.parent_getter("run")

    def get_dataset(self) -> DatasetImporter:
        return self.parent_getter("dataset")

    def get_tomogram(self) -> TomogramImporter:
        return self.parent_getter("tomogram")

    def get_output_path(self) -> str:
        return self.config.get_output_path(self)

    def get_base_metadata(self) -> dict[str, Any]:
        return self.config.get_expanded_metadata(self)

    def get_metadata_path(self) -> str:
        return self.config.get_metadata_path(self)


class VolumeImporter(BaseImporter):
    def __init__(
        self,
        path: str,
        *args: list[Any],
        **kwargs: dict[str, Any],
    ):
        super().__init__(*args, **kwargs)
        self.volume_filename = path

    def get_voxel_size(self) -> np.float32:
        return get_voxel_size(self.config.fs, self.volume_filename)

    def get_header(self) -> MrcObject:
        return get_header(self.config.fs, self.volume_filename)

    def get_output_header(self) -> MrcObject:
        output_prefix = self.get_output_path()
        return get_header(self.config.fs, f"{output_prefix}.mrc")

    def scale_mrcfile(
        self,
        scale_z_axis: bool = True,
        write_zarr: bool = True,
        write_mrc: bool = True,
        voxel_spacing: float | None = None,
    ) -> dict[str, Any]:
        output_prefix = self.get_output_path()
        return scale_mrcfile(
            self.config.fs,
            output_prefix,
            self.volume_filename,
            scale_z_axis=scale_z_axis,
            write_mrc=write_mrc,
            write_zarr=write_zarr,
            header_mapper=self.mrc_header_mapper,
            voxel_spacing=voxel_spacing,
        )

    def get_output_path(self) -> str:
        output_dir = super().get_output_path()
        return os.path.join(output_dir, self.get_run().run_name)

    def load_extra_metadata(self) -> dict[str, Any]:
        run: RunImporter = self.get_run()
        output_prefix = self.get_output_path()
        metadata = get_tomo_metadata(self.config.fs, output_prefix)
        metadata["run_name"] = run.run_name
        return metadata

    def mrc_header_mapper(self, header):
        pass
