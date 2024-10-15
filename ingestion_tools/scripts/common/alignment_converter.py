import os.path
from typing import Any

from cryoet_alignment.io.aretomo3 import AreTomo3ALN
from cryoet_alignment.io.cryoet_data_portal import Alignment
from cryoet_alignment.io.imod import ImodAlignment, ImodNEWSTCOM, ImodTILTCOM, ImodTLT, ImodXF, ImodXTILT
from importers.base_importer import BaseImporter

from common.config import DepositionImportConfig


class BaseAlignmentConverter:

    def __init__(
        self,
        paths: list[str] = None,
        config: DepositionImportConfig = None,
        parents: dict[str, BaseImporter] = None,
        output_prefix: str = "",
    ):
        self.paths = paths
        self.config = config
        self.parents = parents
        self.output_prefix = output_prefix

    def get_alignment_path(self) -> str | None:
        """
        :return: A str path to the alignment file if exists else None
        """
        return None

    def get_tilt_path(self) -> str | None:
        """
        :return: A str path to the tilt file if exists else None
        """
        return None

    def get_tiltx_path(self) -> str | None:
        """
        :return: A str path to the tiltx file if exists else None
        """
        return None

    def get_per_section_alignment_parameters(self) -> list[dict]:
        """
        Generates the per section alignment parameters from the files
        :return: A list of dictionaries containing the per section alignment parameters
        """
        return []

    def _get_files_with_suffix(self, valid_suffix: list[str]) -> str | None:
        for path in self.paths:
            if path.endswith(tuple(valid_suffix)):
                file_name = os.path.basename(path)
                dest_filepath = os.path.join(self.output_prefix, file_name)
                if self.config.fs.exists(dest_filepath):
                    return dest_filepath
        return None


class IMODAlignmentConverter(BaseAlignmentConverter):
    def get_alignment_path(self) -> str | None:
        return self._get_files_with_suffix([".xf"])

    def get_tilt_path(self) -> str | None:
        return self._get_files_with_suffix([".tlt"])

    def get_tiltx_path(self) -> str | None:
        return self._get_files_with_suffix([".tltx", ".xtilt"])

    def get_tiltcom_path(self) -> str | None:
        return self._get_files_with_suffix(["tilt.com"])

    def get_newstcom_path(self) -> str | None:
        return self._get_files_with_suffix(["newst.com"])

    def get_per_section_alignment_parameters(self) -> list[dict]:
        with self.config.fs.open(self.get_alignment_path(), "r") as file:
            xf = ImodXF.from_stream(file)

        with self.config.fs.open(self.get_tilt_path(), "r") as file:
            tlt = ImodTLT.from_stream(file)

        if self.get_tiltx_path() is not None:
            with self.config.fs.open(self.get_tiltx_path(), "r") as file:
                xtilt = ImodXTILT.from_stream(file)
        else:
            xtilt = None

        if self.get_tiltcom_path() is not None:
            with self.config.fs.open(self.get_tiltcom_path(), "r") as file:
                tiltcom = ImodTILTCOM.from_stream(file)
        else:
            tiltcom = None

        if self.get_newstcom_path() is not None:
            with self.config.fs.open(self.get_newstcom_path(), "r") as file:
                newstcom = ImodNEWSTCOM.from_stream(file)
        else:
            newstcom = None

        imod_ali = ImodAlignment(xf=xf, tlt=tlt, xtilt=xtilt, tiltcom=tiltcom, newstcom=newstcom)
        ali = Alignment.from_imod(imod_alignment=imod_ali)
        return [psap.model_dump() for psap in ali.per_section_alignment_parameters]


class AreTomoAlignmentConverter(BaseAlignmentConverter):
    def get_alignment_path(self) -> str | None:
        return self._get_files_with_suffix([".aln"])

    def get_per_section_alignment_parameters(self) -> list[dict]:
        with self.config.fs.open(self.get_alignment_path(), "r") as file:
            aln = AreTomo3ALN.from_stream(file)

        ali = Alignment.from_aretomo3(aln=aln)
        return [psap.model_dump() for psap in ali.per_section_alignment_parameters]


def alignment_converter_factory(
    config: DepositionImportConfig,
    metadata: dict[str, Any],
    paths: list[str],
    parents: dict[str, Any],
    output_prefix: str,
) -> BaseAlignmentConverter:
    alignment_format = metadata.get("format")
    if alignment_format == "IMOD":
        return IMODAlignmentConverter(paths, config, parents, output_prefix)
    elif alignment_format == "ARETOMO3":
        return AreTomoAlignmentConverter(paths, config, parents, output_prefix)

    return BaseAlignmentConverter()
