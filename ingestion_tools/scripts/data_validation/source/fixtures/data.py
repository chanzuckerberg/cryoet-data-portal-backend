import mdocfile
import pandas as pd
import pytest
from data_validation.shared.util import get_tiff_mrc_headers
from importers.collection_metadata import CollectionMetadataImporter
from importers.frame import FrameImporter
from importers.rawtilt import RawTiltImporter
from importers.run import RunImporter
from importers.tiltseries import TiltSeriesImporter
from mrcfile.mrcinterpreter import MrcInterpreter
from tifffile import TiffPage

from common.fs import FileSystemApi, S3Filesystem


@pytest.fixture(scope="session")
def filesystem() -> S3Filesystem:
    return FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)


@pytest.fixture(scope="session")
def frames_files(run: RunImporter) -> list[str]:
    return [
        file_path
        for importer in pytest.cryoet.get_importable_entities(FrameImporter, [run])
        for name, file_path in importer.file_paths.items() if name != "default"
    ]


@pytest.fixture(scope="session")
def tiltseries_files(run: RunImporter) -> list[str]:
    return pytest.cryoet.get_importable_entities(TiltSeriesImporter, [run], "volume_filename")


@pytest.fixture(scope="session")
def frames_headers(frames_files, filesystem: FileSystemApi) -> dict[str, list[TiffPage] | MrcInterpreter]:
    return get_tiff_mrc_headers(frames_files, filesystem)


@pytest.fixture()  # scope="session")
def mdoc_file(run: RunImporter) -> str | None:
    mdoc_files = pytest.cryoet.get_importable_entities(CollectionMetadataImporter, [run], "path")
    if len(mdoc_files) == 1:
        return mdoc_files[0]
    elif len(mdoc_files) > 1:
        pytest.fail(f"Multiple mdoc files found: {mdoc_files}")
    return None


@pytest.fixture()  # scope="session")
def mdoc_data(filesystem: S3Filesystem, mdoc_file: str) -> pd.DataFrame:
    if not mdoc_file:
        pytest.skip("No mdoc files found")
    local_filepath = filesystem.localreadable(mdoc_file)
    return mdocfile.read(local_filepath)


@pytest.fixture()  # scope="session")
def raw_tlt_file(run: RunImporter) -> str | None:
    raw_tilt_files = pytest.cryoet.get_importable_entities(RawTiltImporter, [run], "path")
    if len(raw_tilt_files) == 1:
        return raw_tilt_files[0]
    elif len(raw_tilt_files) > 1:
        pytest.fail(f"Multiple raw tlt files found: {raw_tilt_files}")
    return None


@pytest.fixture()  # scope="session")
def raw_tilt_data(filesystem: S3Filesystem, raw_tlt_file: str) -> pd.DataFrame:
    if not raw_tlt_file:
        pytest.skip("No raw_tilt files found")
    local_filepath = filesystem.localreadable(raw_tlt_file)
    with open(local_filepath, "r") as f:
        return pd.read_csv(f, sep=r"\s+", header=None, names=["TiltAngle"])
