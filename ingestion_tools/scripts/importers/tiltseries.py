import os.path
from typing import Any

import pandas as pd
from mdocfile.data_models import MdocSectionData

from common.config import DepositionImportConfig
from common.ctf_converter import CTFInfo
from common.finders import DefaultImporterFactory
from common.id_helper import IdentifierHelper
from common.metadata import TiltSeriesMetadata
from importers.base_importer import VolumeImporter
from importers.collection_metadata import CollectionMetadataImporter
from importers.ctf import CtfImporter
from importers.frame import FrameImporter
from importers.rawtilt import RawTiltImporter


class TiltSeriesIdentifierHelper(IdentifierHelper):
    @classmethod
    def _get_container_key(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        return "-".join(["tiltseries", parents["run"].get_output_path()])

    @classmethod
    def _get_metadata_glob(cls, config: DepositionImportConfig, parents: dict[str, Any], *args, **kwargs) -> str:
        run = parents["run"]
        metadata_glob = config.resolve_output_path("tiltseries_metadata", run, {"tiltseries_id": "*"})
        return metadata_glob

    @classmethod
    def _generate_hash_key(
        cls,
        container_key: str,
        metadata: dict[str, Any],
        parents: dict[str, Any],
        *args,
        **kwargs,
    ) -> str:
        return "-".join(
            [
                container_key,
                str(metadata.get("deposition_id", int(parents["deposition"].name))),
            ],
        )


class TiltSeriesImporter(VolumeImporter):
    type_key = "tiltseries"
    plural_key = "tiltseries"
    finder_factory = DefaultImporterFactory
    has_metadata = True
    dir_path = "{dataset_name}/{run_name}/TiltSeries/{tiltseries_id}"
    metadata_path = os.path.join(dir_path, "tiltseries_metadata.json")

    def __init__(
        self,
        config: DepositionImportConfig,
        metadata: dict[str, Any],
        name: str,
        path: str,
        allow_imports: bool,
        parents: dict[str, Any],
    ):
        super().__init__(
            config=config,
            metadata=metadata,
            name=name,
            path=path,
            parents=parents,
            allow_imports=allow_imports,
        )
        self.identifier = TiltSeriesIdentifierHelper.get_identifier(config, self.get_base_metadata(), self.parents)

    def import_item(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name}")
            return
        _ = self.scale_mrcfile(
            scale_z_axis=False,
            write_mrc=self.config.write_mrc,
            write_zarr=self.config.write_zarr,
            voxel_spacing=self.get_pixel_spacing(),
        )

    def get_frames_count(self) -> int:
        num_frames = 0
        for importer in FrameImporter.finder(self.config, **self.parents):
            num_frames += importer.get_frame_count()
        return num_frames

    def import_metadata(self) -> None:
        if not self.is_import_allowed():
            print(f"Skipping import of {self.name} metadata")
            return
        dest_ts_metadata = self.get_metadata_path()
        merge_data = self.load_extra_metadata()
        merge_data["frames_count"] = self.get_frames_count()
        base_metadata = self.get_base_metadata()
        merge_data["pixel_spacing"] = self.get_pixel_spacing()
        psp_generator = PerSectionParameterGenerator(self.config, {**self.parents, "tiltseries": self})
        merge_data["per_section_parameter"] = psp_generator.get_data()
        merge_data["raw_tlt_path"] = psp_generator.get_raw_tlt_path()
        merge_data["ctf_path"] = psp_generator.get_ctf_path()
        metadata = TiltSeriesMetadata(self.config.fs, self.get_deposition().name, base_metadata)
        metadata.write_metadata(dest_ts_metadata, merge_data)

    def get_pixel_spacing(self) -> float:
        pixel_spacing = self.get_base_metadata().get("pixel_spacing")
        if pixel_spacing:
            return float(pixel_spacing)
        return round(self.get_voxel_size(), 3)

    def mrc_header_mapper(self, header) -> None:
        header.ispg = 0
        header.mz = 1
        header.cella.z = 1 * self.get_pixel_spacing()

    @classmethod
    def get_name_and_path(cls, metadata: dict, name: str, path: str, results: dict[str, str]) -> [str, str, dict]:
        filename = metadata.get("omezarr_dir")
        complete_path = os.path.join(os.path.dirname(path), filename)
        return filename, complete_path, {filename: complete_path}

class PerSectionParameter:

    def __init__(self, index: int, mdoc_entry: MdocSectionData, ctf_entry: CTFInfo):
        self.z_index = index
        self.frame_acquisition_order = mdoc_entry.ZValue
        self.raw_angle = mdoc_entry.TiltAngle

        self.astigmatic_angle = ctf_entry.azimuth if ctf_entry else None
        self.cross_correlation = ctf_entry.cross_correlation if ctf_entry else None
        self.major_defocus = ctf_entry.defocus_1 if ctf_entry else None
        self.max_resolution = ctf_entry.max_resolution if ctf_entry else None
        self.minor_defocus = ctf_entry.defocus_2 if ctf_entry else None
        self.phase_shift = ctf_entry.phase_shift if ctf_entry else None

    def to_json(self) -> dict[str, Any]:
        return self.__dict__

class PerSectionParameterGenerator:
    def __init__(self, config: DepositionImportConfig, parents: dict[str, Any]):
        self.config = config
        self.parents = parents
        self.raw_tlt_dest_file = self._get_raw_tlt_dest()
        self.ctf_importer = self._get_ctf_importer()

    def get_data(self) -> list[dict[str, str]]:
        psp = []
        rawtlt = self._get_raw_tlt()
        mdoc_data = self._get_mdoc_data()
        ctf_data = self._get_ctf_data()
        for index, raw_angle in rawtlt["raw_tlt_angle"].items():
            mdoc_entry = self._get_mdoc_entry(round(raw_angle), mdoc_data)
            ctf_entry = self._get_ctf_entry(mdoc_entry.ZValue, ctf_data)
            psp_section = PerSectionParameter(index, mdoc_entry, ctf_entry)
            psp.append(psp_section.to_json())

        return psp

    def get_raw_tlt_path(self) -> str:
        return self.config.to_formatted_path(self.raw_tlt_dest_file)

    def get_ctf_path(self) -> str | None:
        return self.config.to_formatted_path(self.ctf_importer.get_destination_path()) if self.ctf_importer else None

    def _get_raw_tlt_dest(self) -> str:
        for rawtlt in RawTiltImporter.finder(self.config, **self.parents):
            if not rawtlt.path or not rawtlt.path.endswith(".rawtlt"):
                # Check to prevent any other files being included in the rawtlt section, incorrectly being pulled here.
                continue
            return rawtlt.get_destination_path()
        raise FileNotFoundError(f"No rawtlt found for run: {self.parents['run'].name}")

    def _get_raw_tlt(self) -> pd.DataFrame:
        local_path = self.config.fs.localreadable(self.raw_tlt_dest_file)
        return pd.read_csv(local_path, names=["raw_tlt_angle"])

    def _get_ctf_importer(self) -> CtfImporter | None:
        for ctf in CtfImporter.finder(self.config, **self.parents):
            return ctf
        return None

    def _get_ctf_data(self) -> list[CTFInfo]:
        if self.ctf_importer:
            return self.ctf_importer.get_output_data()
        return []

    @classmethod
    def _get_ctf_entry(cls, section_id: int, ctf_data: list[CTFInfo]) -> CTFInfo | None:
        for entry in ctf_data:
            # To offset the ctf data's section index starts at 1.
            section_index = entry.section - 1
            if section_id == section_index:
                return entry
        return None

    def _get_mdoc_data(self) -> list[MdocSectionData]:
        collection_md = CollectionMetadataImporter.get_importer(self.config, **self.parents)
        return collection_md.get_output_data().section_data

    @classmethod
    def _get_mdoc_entry(cls, tilt_angle: float, mdoc_data: list[MdocSectionData]) -> MdocSectionData:
        for entry in mdoc_data:
            if round(entry.TiltAngle) == tilt_angle:
                return entry
        raise KeyError(f"No match for tiltangle {tilt_angle} in mdoc_data")
