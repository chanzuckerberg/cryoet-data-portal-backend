import pytest
from data_validation.helpers.util import get_tiff_mrc_headers
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
def frame_files(run: RunImporter) -> list[str]:
    return pytest.cryoet.get_importable_entities(FrameImporter, [run], "path")

@pytest.fixture(scope="session")
def tiltseries_files(run: RunImporter) -> list[str]:
    return pytest.cryoet.get_importable_entities(TiltSeriesImporter, [run], "volume_filename")

@pytest.fixture(scope="session")
def frames_headers(frame_files: list[str], filesystem: FileSystemApi) -> dict[str, list[TiffPage]| MrcInterpreter]:
    return get_tiff_mrc_headers(frame_files, filesystem)


@pytest.fixture(scope="session")
def mdoc_files(run: RunImporter) -> list[str]:
    return pytest.cryoet.get_importable_entities(CollectionMetadataImporter, [run], "path")
