"""
Any fixtures involving loading data from the bucket.
"""

import json
from typing import Dict, List

import mdocfile
import ndjson
import pandas as pd
import pytest
import zarr
from mrcfile.mrcinterpreter import MrcInterpreter
from ome_zarr.io import ZarrLocation

from common.fs import FileSystemApi

# ==================================================================================================
# Helper functions
# ==================================================================================================


def get_header(mrcfile: str, fs: FileSystemApi) -> MrcInterpreter:
    """Get the mrc file headers for a list of mrc files."""
    try:
        with fs.open(mrcfile, "rb") as f:
            header = MrcInterpreter(iostream=f, permissive=True, header_only=True)
        return header
    except Exception as _:
        pytest.fail(f"Failed to get header for {mrcfile}")


def get_zarr_headers(zarrfile: str, fs: FileSystemApi) -> Dict[str, Dict]:
    """Get the zattrs and zarray data for a zarr volume file."""
    expected_subfolders = {f"{zarrfile}/{i}" for i in range(3)}.union({f"{zarrfile}/.zattrs", f"{zarrfile}/.zgroup"})
    actual_subfolders = {"s3://" + folder for folder in fs.glob(zarrfile + "/*")}
    if expected_subfolders != actual_subfolders:
        pytest.fail(f"Expected zarr subfolders: {expected_subfolders}, Actual zarr subfolders: {actual_subfolders}")

    fsstore = zarr.storage.FSStore(url=zarrfile, mode="r", fs=fs.s3fs, dimension_separator="/")
    fsstore_subfolders = set(fsstore.listdir())
    expected_fsstore_subfolders = {str(i) for i in range(3)}.union({".zattrs", ".zgroup"})
    if expected_fsstore_subfolders != fsstore_subfolders:
        pytest.fail(f"Expected zarr subfolders: {expected_subfolders}, Actual zarr subfolders: {fsstore_subfolders}")

    loc = ZarrLocation(fsstore)
    zarrays = {}
    for i in range(3):
        zarrays[i] = json.loads(fsstore[str(i) + "/.zarray"].decode())
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
# Tiltseries fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def tiltseries_mrc_header(tiltseries_mrc_file: str, filesystem: FileSystemApi) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for a tilt series."""
    return get_header(tiltseries_mrc_file, filesystem)


@pytest.fixture(scope="session")
def tiltseries_metadata(tiltseries_meta_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the tiltseries metadata."""
    with filesystem.open(tiltseries_meta_file, "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def tiltseries_mdoc(tiltseries_mdoc_file: str, filesystem: FileSystemApi) -> pd.DataFrame:
    """Load the tiltseries mdoc."""
    with filesystem.open(tiltseries_mdoc_file, "r") as f:
        return mdocfile.read(f)


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
    return get_header(canonical_tomo_mrc_file, filesystem)


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
        headers[mrc_filename] = get_header(mrc_filename, filesystem)

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
