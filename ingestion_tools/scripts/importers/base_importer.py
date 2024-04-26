import contextlib
import os
from typing import TYPE_CHECKING, Any, Optional

import numpy as np
from mrcfile.mrcobject import MrcObject

from common.finders import DepositionObjectImporterFactory
from common.image import get_header, get_tomo_metadata, get_voxel_size, scale_mrcfile

if TYPE_CHECKING:
    from common.config import DepositionImportConfig
    from common.fs import FileSystemApi
    from importers.dataset import DatasetImporter
    from importers.run import RunImporter
    from importers.tomogram import TomogramImporter
else:
    RunImporter = "RunImporter"
    DatasetImporter = "DatasetImporter"
    TomogramImporter = "TomogramImporter"
    DepositionImportConfig = "DepositionImportConfig"
    FileSystemApi = "FileSystemApi"


class BaseImporter:
    type_key: str
    cached_find_results: dict[str, "BaseImporter"] = {}
    finder_factory: DepositionObjectImporterFactory | None = None
    dependencies: list[str] = []

    def __init__(
        self,
        config: "DepositionImportConfig",
        name: Optional[str] = None,
        path: Optional[str] = None,
        parents: Optional["BaseImporter"] = None,
    ):
        self.config = config
        self.parents = parents
        self.name = name
        self.path = path

    def parent_getter(self, type_key: str) -> "BaseImporter":
        if self.type_key == type_key:
            return self
        for parent in self.parents:
            item = parent.parent_getter(type_key)
            if item:
                return item

    def get_glob_vars(self) -> dict[str, Any]:
        glob_vars = {}
        glob_vars[f"{self.type_key}_path"] = self.path
        glob_vars[f"{self.type_key}_name"] = self.name
        with contextlib.suppress(ValueError, TypeError):
            glob_vars[f"int_{self.type_key}_name"] = int(self.name)

        # TODO FIXME this should probably be moved to the RunImporter
        if self.type_key == "run":
            run_name = self.name
            glob_vars.update(self.config.get_run_data_map(run_name))

            # TODO: remove these in favor of the singular tsv file
            glob_vars["mapped_tomo_name"] = self.config.run_to_tomo_map.get(run_name)
            glob_vars["mapped_frame_name"] = self.config.run_to_frame_map.get(run_name)
            glob_vars["mapped_ts_name"] = self.config.run_to_ts_map.get(run_name)

        if self.parents:
            for parent in self.parents.values():
                glob_vars.update(parent.get_glob_vars())
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

    @classmethod
    def finder(cls, config: DepositionImportConfig, fs: FileSystemApi, **parents) -> list["BaseImporter"]:
        finder_configs = config._get_finder_configs(cls.type_key, **parents)
        for config in finder_configs:
            finder_cls = cls.finder_factory.load(**config)
            yield (item for item in finder_cls.find(cls, config, fs, **parents))

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
        return os.path.join(output_dir, self.get_run().name)

    def load_extra_metadata(self) -> dict[str, Any]:
        run: RunImporter = self.get_run()
        output_prefix = self.get_output_path()
        metadata = get_tomo_metadata(self.config.fs, output_prefix)
        metadata["run_name"] = run.name
        return metadata

    def mrc_header_mapper(self, header):
        pass


class BaseFileImporter(BaseImporter):
    def import_item(self, write: bool = True):
        fs = self.config.fs
        output_dir = self.get_output_path()
        dest_filename = os.path.join(output_dir, os.path.basename(self.path))
        fs.copy(self.path, dest_filename)
