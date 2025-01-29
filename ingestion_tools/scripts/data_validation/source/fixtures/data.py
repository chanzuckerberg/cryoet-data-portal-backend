import mdocfile
import pandas as pd
import pytest
from data_validation.shared.util import get_tiff_mrc_headers
from importers.collection_metadata import CollectionMetadataImporter
from importers.frame import FrameImporter
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
    return pytest.cryoet.get_importable_entities(FrameImporter, [run], "path")

@pytest.fixture(scope="session")
def tiltseries_files(run: RunImporter) -> list[str]:
    return pytest.cryoet.get_importable_entities(TiltSeriesImporter, [run], "volume_filename")

@pytest.fixture(scope="session")
def frames_headers(frames_files, filesystem: FileSystemApi) -> dict[str, list[TiffPage] | MrcInterpreter]:
    return get_tiff_mrc_headers(frames_files, filesystem)


@pytest.fixture(scope="session")
def mdoc_file(run: RunImporter) -> str:
    mdoc_files = pytest.cryoet.get_importable_entities(CollectionMetadataImporter, [run], "path")
    if len(mdoc_files) == 1:
        return mdoc_files[0]
    elif len(mdoc_files) > 1:
        pytest.fail(f"Multiple mdoc files found: {mdoc_files}")
    return None


@pytest.fixture(scope="session")
def mdoc_data(filesystem: S3Filesystem, mdoc_file: str) -> pd.DataFrame:
    if not mdoc_file:
        pytest.skip("No mdoc files found")
    return mdocfile.read(filesystem.localreadable(mdoc_file))
