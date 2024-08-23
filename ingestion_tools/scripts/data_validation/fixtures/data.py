"""
Any fixtures involving loading data from the bucket.
"""

import bz2
import io
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Union

import mdocfile
import ndjson
import pandas as pd
import pytest
import tifffile
import zarr
from mrcfile.mrcinterpreter import MrcInterpreter
from ome_zarr.io import ZarrLocation

from common.fs import FileSystemApi

# ==================================================================================================
# Helper functions
# ==================================================================================================

# block sizes are experimentally tested to be the fastest
MRC_HEADER_BLOCK_SIZE = 500 * 2**10
TIFF_HEADER_BLOCK_SIZE = 100 * 2**10


def get_mrc_header(mrcfile: str, fs: FileSystemApi) -> MrcInterpreter:
    """Get the mrc file headers for a list of mrc files."""
    try:
        with fs.open(mrcfile, "rb", block_size=MRC_HEADER_BLOCK_SIZE) as f:
            return MrcInterpreter(iostream=f, permissive=True, header_only=True)
    except Exception as e:
        pytest.fail(f"Failed to get header for {mrcfile}: {e}")


def get_mrc_bz2_header(mrcbz2file: str, fs: FileSystemApi) -> MrcInterpreter:
    """Get the mrc file headers for a list of mrc files."""
    try:
        with fs.open(mrcbz2file, "rb", block_size=MRC_HEADER_BLOCK_SIZE) as f, bz2.BZ2File(f) as mrcbz2:
            mrcbz2 = mrcbz2.read(MRC_HEADER_BLOCK_SIZE)
            return MrcInterpreter(iostream=io.BytesIO(mrcbz2), permissive=True, header_only=True)
    except Exception as e:
        pytest.fail(f"Failed to get header for {mrcbz2file}: {e}")


def get_zarr_headers(zarrfile: str, fs: FileSystemApi) -> Dict[str, Dict]:
    """Get the zattrs and zarray data for a zarr volume file."""
    expected_children = {f"{child}" for child in [0, 1, 2, ".zattrs", ".zgroup"]}

    fsstore = zarr.storage.FSStore(url=zarrfile, mode="r", fs=fs.s3fs, dimension_separator="/")
    fsstore_children = set(fsstore.listdir())
    expected_fsstore_children = {"0", "1", "2", ".zattrs", ".zgroup"}
    if expected_fsstore_children != fsstore_children:
        pytest.fail(f"Expected zarr children: {expected_children}, Actual zarr children: {fsstore_children}")

    loc = ZarrLocation(fsstore)
    zarrays = {}
    for binning_factor in [0, 1, 2]:  # 1x, 2x, 4x
        zarrays[binning_factor] = json.loads(fsstore[str(binning_factor) + "/.zarray"].decode())
    return {"zattrs": loc.root_attrs, "zarrays": zarrays}


# ==================================================================================================
# Dataset fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def dataset_metadata(dataset_metadata_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the dataset metadata."""
    with filesystem.open(dataset_metadata_file, "r") as f:
        return json.load(f)


# ==================================================================================================
# Frame fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def frames_headers(
    frames_files: List[str],
    filesystem: FileSystemApi,
) -> Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]:
    """Get the headers for a list of frame files."""

    def open_frame(frame_file: str):
        if frame_file.endswith(".mrc"):
            return (frame_file, get_mrc_header(frame_file, filesystem))
        elif frame_file.endswith(".mrc.bz2"):
            return (frame_file, get_mrc_bz2_header(frame_file, filesystem))
        elif frame_file.endswith(".tif") or frame_file.endswith(".tiff") or frame_file.endswith(".eer"):
            with filesystem.open(frame_file, "rb", block_size=TIFF_HEADER_BLOCK_SIZE) as f, tifffile.TiffFile(f) as tif:
                # The tif.pages must be converted to a list to actually read all the pages' data
                return (frame_file, list(tif.pages))
        else:
            return (None, None)

    # Open the images in parallel
    with ThreadPoolExecutor() as executor:
        headers = {}

        for header_filename, header_data in executor.map(open_frame, frames_files):
            if header_filename is None:
                continue
            headers[header_filename] = header_data

        if not headers:
            pytest.skip("No file-format supported frames headers found")

        return headers


# ==================================================================================================
# Gain fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def gain_mrc_header(gain_file: str, filesystem: FileSystemApi) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for a gain file."""
    if not gain_file.endswith(".mrc"):
        pytest.skip(f"Not an mrc file, skipping mrc checks: {gain_file}")

    return {gain_file: get_mrc_header(gain_file, filesystem)}


# ==================================================================================================
# Tiltseries fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def tiltseries_mrc_header(tiltseries_mrc_file: str, filesystem: FileSystemApi) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for a tilt series."""
    return get_mrc_header(tiltseries_mrc_file, filesystem)


@pytest.fixture(scope="session")
def tiltseries_metadata(tiltseries_meta_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the tiltseries metadata."""
    with filesystem.open(tiltseries_meta_file, "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def tiltseries_mdoc(tiltseries_mdoc_files: str, filesystem: FileSystemApi) -> pd.DataFrame:
    """Load the tiltseries mdoc files and return a concatenated DataFrame."""
    tiltseries_dataframes = [mdocfile.read(filesystem.localreadable(mdoc_file)) for mdoc_file in tiltseries_mdoc_files]
    tiltseries_merged = pd.concat(tiltseries_dataframes, ignore_index=True)
    return tiltseries_merged


@pytest.fixture(scope="session")
def tiltseries_tlt(tiltseries_tlt_file: str, filesystem: FileSystemApi) -> pd.DataFrame:
    """Load the tiltseries tlt."""
    with filesystem.open(tiltseries_tlt_file, "r") as f:
        return pd.read_csv(f, sep=r"\s+", header=None, names=["tilt_angle"])


# ==================================================================================================
# Tomogram fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def canonical_tomo_mrc_headers(canonical_tomo_mrc_file: str, filesystem: FileSystemApi) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for a tomogram."""
    return get_mrc_header(canonical_tomo_mrc_file, filesystem)


@pytest.fixture(scope="session")
def canonical_tomogram_metadata(canonical_tomo_meta_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the canonical tomogram metadata."""
    with filesystem.open(canonical_tomo_meta_file, "r") as f:
        return json.load(f)


# ==================================================================================================
# Annotation fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def annotation_metadata(annotation_metadata_files: List[str], filesystem: FileSystemApi) -> Dict[str, Dict]:
    """Load the annotation metadata. Dictionary structure: metadata = {metadata_a_filename: Dict}, metadata_b_filename: ...}."""
    metadata_objs = {}

    for file in annotation_metadata_files:
        with filesystem.open(file, "r") as f:
            metadata_objs[file] = json.load(f)

    return metadata_objs


def get_ndjson_annotations(
    annotation_files: List[str],
    filesystem: FileSystemApi,
) -> Dict[str, List[Dict]]:
    """
    A helper function to load ndjson annotations (a list of annotations, with each annotation being a Dict)
    for point, oriented point, and instance segmentation annotations.
    Dictionary structure: annotations = {annotation_a_filename: List[Dict], annotation_b_filename: List[Dict]}.
    """
    annotations = {}
    # Only need the annotation file to find the annotations.
    for annotation_file in annotation_files:
        with filesystem.open(annotation_file, "r") as f:
            annotations[annotation_file] = ndjson.load(f)

    return annotations


@pytest.fixture(scope="session")
def point_annotations(
    point_annotation_files: List[str],
    filesystem: FileSystemApi,
) -> Dict[str, List[Dict]]:
    """Load point annotations."""
    return get_ndjson_annotations(point_annotation_files, filesystem)


@pytest.fixture(scope="session")
def oriented_point_annotations(
    oriented_point_annotation_files: List[str],
    filesystem: FileSystemApi,
) -> Dict[str, List[Dict]]:
    """Load oriented point annotations."""
    return get_ndjson_annotations(oriented_point_annotation_files, filesystem)


@pytest.fixture(scope="session")
def instance_seg_annotations(
    instance_seg_annotation_files: List[str],
    filesystem: FileSystemApi,
) -> Dict[str, List[Dict]]:
    """Load instance segmentation annotations."""
    return get_ndjson_annotations(instance_seg_annotation_files, filesystem)


@pytest.fixture(scope="session")
def seg_mask_annotation_mrc_headers(
    seg_mask_annotation_mrc_files: List[str],
    filesystem: FileSystemApi,
) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for an mrc annotation file."""
    headers = {}
    for mrc_filename in seg_mask_annotation_mrc_files:
        headers[mrc_filename] = get_mrc_header(mrc_filename, filesystem)

    return headers


@pytest.fixture(scope="session")
def seg_mask_annotation_zarr_headers(
    seg_mask_annotation_zarr_files: List[str],
    filesystem: FileSystemApi,
) -> Dict[str, Dict[str, Dict]]:
    """
    Get the zattrs and zarray data for a zarr annotation file.
    Dictionary structure: headers = {annotation_a_filename: {"zattrs": Dict, "zarrays": Dict}}, annotation_b_filename: ...}.
    """
    headers = {}
    for zarr_filename in seg_mask_annotation_zarr_files:
        headers[zarr_filename] = get_zarr_headers(zarr_filename, filesystem)

    return headers
