import bz2
import io
import json
import os
from concurrent.futures import ThreadPoolExecutor

import pytest
from mrcfile.mrcinterpreter import MrcInterpreter
from tifffile import TiffFile, TiffPage

from common.fs import FileSystemApi

# block sizes are experimentally tested to be the fastest
MRC_HEADER_BLOCK_SIZE = 2 * 2**10
MRC_BZ2_HEADER_BLOCK_SIZE = 500 * 2**10
TIFF_HEADER_BLOCK_SIZE = 100 * 2**10

PERMITTED_FRAME_EXTENSIONS = [".mrc", ".tif", ".tiff", ".eer", ".mrc.bz2"]
PERMITTED_GAIN_EXTENSIONS = PERMITTED_FRAME_EXTENSIONS + [".gain"]
MRC_EXTENSION = ".mrc"
MRC_BZ2_EXTENSION = ".mrc.bz2"
TIFF_EXTENSIONS = (".tif", ".tiff", ".eer", ".gain")


def get_file_type(filename: str) -> str:
    if filename.endswith(".zarr"):
        return "zarr"
    if any(filename.endswith(extension) for extension in [".mrc", ".st", ".ali", ".mrcs"]):
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
    """Get the metadata of a Zarr v3 / OME-NGFF 0.5 image written by the Portal.

    Returns ``{"zattrs": <OME metadata: attributes.ome>, "zarrays": {level: <the level's zarr.json>},
    "group": <the group's zarr.json>, "image_type": <dca.image_type or None>}``; ``zarrays`` is keyed by the integer
    level, 0, 1, ..., K.
    """

    def fail(message: str) -> None:
        if fail_test:
            pytest.fail(message)

    file_paths = fs.glob(os.path.join(zarrfile, "*"))
    fsstore_children = {os.path.basename(file) for file in file_paths}
    if "zarr.json" not in fsstore_children or fsstore_children & {".zgroup", ".zattrs", ".zarray"}:
        fail(f"Expected a Zarr v3 group (zarr.json and no Zarr v2 metadata), Actual children: {fsstore_children}")
        return None
    with fs.open(os.path.join(zarrfile, "zarr.json"), "r") as f:
        group = json.load(f)
    ome = group.get("attributes", {}).get("ome", {})
    levels = [d["path"] for d in ome.get("multiscales", [{}])[0].get("datasets", [])]
    expected_children = {"zarr.json", *levels}
    if expected_children != fsstore_children:
        fail(f"Expected zarr children: {expected_children}, Actual children: {fsstore_children}")
        return None

    zarrays = {}
    for level in levels:
        with fs.open(os.path.join(zarrfile, level, "zarr.json"), "r") as f:
            zarrays[int(level)] = json.load(f)
    return {
        "zattrs": ome,
        "zarrays": zarrays,
        "group": group,
        "image_type": group.get("attributes", {}).get("dca", {}).get("image_type"),
    }


def get_mrc_bz2_header(mrcbz2file: str, fs: FileSystemApi, fail_test: bool = True) -> MrcInterpreter:
    """Get the mrc file headers for a list of mrc files."""
    try:
        with fs.open(mrcbz2file, "rb", block_size=MRC_BZ2_HEADER_BLOCK_SIZE) as f, bz2.BZ2File(f) as mrcbz2:
            mrcbz2 = mrcbz2.read(MRC_BZ2_HEADER_BLOCK_SIZE)
            return MrcInterpreter(iostream=io.BytesIO(mrcbz2), permissive=True, header_only=True)
    except Exception as e:
        if fail_test:
            pytest.fail(f"Failed to get header for {mrcbz2file}: {e}")
        else:
            return None


def _get_tiff_mrc_header(file: str, filesystem: FileSystemApi, fail_test: bool = True):
    if file.endswith(MRC_EXTENSION):
        return file, get_mrc_header(file, filesystem, fail_test)
    if file.endswith(MRC_BZ2_EXTENSION):
        return file, get_mrc_bz2_header(file, filesystem, fail_test)
    if file.endswith(TIFF_EXTENSIONS):
        with filesystem.open(file, "rb", block_size=TIFF_HEADER_BLOCK_SIZE) as f, TiffFile(f) as tif:
            # The tif.pages must be converted to a list to actually read all the pages' data
            return file, list(tif.pages)
    return None, None


def get_tiff_mrc_headers(
    files: list[str],
    filesystem: FileSystemApi,
    fail_test: bool = True,
) -> dict[str, list[TiffPage] | MrcInterpreter]:

    # Open the images in parallel
    with ThreadPoolExecutor() as executor:
        headers = {}

        for header_filename, header_data in executor.map(
            _get_tiff_mrc_header,
            files,
            [filesystem] * len(files),
            [fail_test] * len(files),
        ):
            if header_filename is None:
                continue
            headers[header_filename] = header_data

        return headers
