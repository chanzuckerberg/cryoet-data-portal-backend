import bz2
import io
import json
import os
from concurrent.futures import ThreadPoolExecutor

import pytest
from mrcfile.mrcinterpreter import MrcInterpreter
from tifffile import TiffFile, TiffPage

from common.fs import FileSystemApi

BINNING_FACTORS = [0, 1, 2]
# block sizes are experimentally tested to be the fastest
MRC_HEADER_BLOCK_SIZE = 2 * 2**10
MRC_BZ2_HEADER_BLOCK_SIZE = 500 * 2**10
TIFF_HEADER_BLOCK_SIZE = 100 * 2**10

PERMITTED_FRAME_EXTENSIONS = [".mrc", ".tif", ".tiff", ".eer", ".mrc.bz2"]
PERMITTED_GAIN_EXTENSIONS = PERMITTED_FRAME_EXTENSIONS + [".gain"]


def get_file_type(filename: str) -> str:
    if filename.endswith(".zarr"):
        return "zarr"
    elif any(filename.endswith(extension) for extension in [".mrc", ".st"]):
        return "mrc"
    return "unknown"

def get_mrc_header(mrc_file_path: str, fs: FileSystemApi, fail_test: bool = True) -> MrcInterpreter | None:
    try:
        """Get the mrc file headers for a mrc file."""
        with fs.open(mrc_file_path, "rb", block_size=MRC_HEADER_BLOCK_SIZE) as f:
            return MrcInterpreter(iostream=f, permissive=True, header_only=True)
    except Exception as e:
        if fail_test:
            pytest.fail(f"Failed to get header for {mrc_file_path}: {e}")
        return None


def get_zarr_metadata(zarrfile: str, fs: FileSystemApi, fail_test: bool = True) -> dict[str, dict] | None:
    """Get the zattrs and zarray data for a zarr volume file."""
    file_paths = fs.glob(os.path.join(zarrfile, "*"))
    fsstore_children = {os.path.basename(file) for file in file_paths}
    expected_fsstore_children = {"0", "1", "2", ".zattrs", ".zgroup"}
    if expected_fsstore_children != fsstore_children:
        if fail_test:
            pytest.fail(f"Expected zarr children: {expected_fsstore_children}, Actual children: {fsstore_children}")
        else:
            return None

    zarrays = {}
    for binning in BINNING_FACTORS:
        with fs.open(os.path.join(zarrfile, str(binning), ".zarray"), "r") as f:
            zarrays[binning] = json.load(f)
    with fs.open(os.path.join(zarrfile, ".zattrs"), "r") as f:
        return {"zattrs": json.load(f), "zarrays": zarrays}


def get_mrc_bz2_header(mrcbz2file: str, fs: FileSystemApi) -> MrcInterpreter:
    """Get the mrc file headers for a list of mrc files."""
    try:
        with fs.open(mrcbz2file, "rb", block_size=MRC_BZ2_HEADER_BLOCK_SIZE) as f, bz2.BZ2File(f) as mrcbz2:
            mrcbz2 = mrcbz2.read(MRC_BZ2_HEADER_BLOCK_SIZE)
            return MrcInterpreter(iostream=io.BytesIO(mrcbz2), permissive=True, header_only=True)
    except Exception as e:
        pytest.fail(f"Failed to get header for {mrcbz2file}: {e}")



def _get_tiff_mrc_header(file: str, filesystem: FileSystemApi):
    if file.endswith(".mrc"):
        return file, get_mrc_header(file, filesystem)
    elif file.endswith(".mrc.bz2"):
        return file, get_mrc_bz2_header(file, filesystem)
    elif file.endswith((".tif", ".tiff", ".eer", ".gain")):
        with filesystem.open(file, "rb", block_size=TIFF_HEADER_BLOCK_SIZE) as f, TiffFile(f) as tif:
            # The tif.pages must be converted to a list to actually read all the pages' data
            return file, list(tif.pages)
    else:
        return None, None


def get_tiff_mrc_headers(
    files: list[str], filesystem: FileSystemApi,
) -> dict[str, list[TiffPage]| MrcInterpreter]:

    # Open the images in parallel
    with ThreadPoolExecutor() as executor:
        headers = {}

        for header_filename, header_data in executor.map(_get_tiff_mrc_header, files, [filesystem] * len(files)):
            if header_filename is None:
                continue
            headers[header_filename] = header_data

        return headers
