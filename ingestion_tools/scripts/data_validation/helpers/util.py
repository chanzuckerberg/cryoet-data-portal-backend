import json
import os

import pytest
from mrcfile.mrcinterpreter import MrcInterpreter

from common.fs import FileSystemApi

BINNING_FACTORS = [0, 1, 2]
# block sizes are experimentally tested to be the fastest
MRC_HEADER_BLOCK_SIZE = 2 * 2**10


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
