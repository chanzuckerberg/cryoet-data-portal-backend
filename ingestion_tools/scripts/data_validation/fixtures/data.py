"""
Any fixtures involving loading data from the bucket.
"""

import json
from typing import Dict, List

import mdocfile
import ndjson
import pandas as pd
import pytest
from mrcfile.mrcinterpreter import MrcInterpreter

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


def get_zattrs(zarrfile: str, fs: FileSystemApi) -> Dict:
    """Get the zattrs for a zarr volume file without downloading the entire file."""
    with fs.open(zarrfile + "/.zattrs", "r") as f:
        zattrs = json.load(f)
    return zattrs


def get_zarrays(zarrfile: str, fs: FileSystemApi) -> Dict:
    """Get the zarray for a zarr volume file without downloading the entire file."""
    zarrays = {}
    for i in range(3):
        with fs.open(zarrfile + f"/{i}/.zarray", "r") as f:
            zarrays[i] = json.load(f)
    return zarrays


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
    """Load the annotation metadata. Dictionary structure: metadata = {annotation_a_filename: {metadata_a_filename: Dict}, annotation_b_filename: ...}."""
    metadata_objs = {}

    for file in annotation_metadata_files:
        with filesystem.open(file, "r") as f:
            metadata_objs[file] = json.load(f)

    return metadata_objs


def get_ndjson_annotations(annotation_files: Dict[str, str], filesystem: FileSystemApi) -> Dict[str, List[Dict]]:
    """Load ndjson annotations. Dictionary structure: annotations = {annotation_a_filename: Dict, annotation_b_filename: ...}."""
    annotations = {}
    for annotation_file, _ in annotation_files.items():
        with filesystem.open(annotation_file, "r") as f:
            annotations[annotation_file] = ndjson.load(f)

    return annotations


@pytest.fixture(scope="session")
def point_annotations(
    point_annotation_files_to_metadata_files: Dict[str, str],
    filesystem: FileSystemApi,
) -> Dict[str, List[Dict]]:
    """Load point annotations."""
    return get_ndjson_annotations(point_annotation_files_to_metadata_files, filesystem)


@pytest.fixture(scope="session")
def oriented_point_annotations(
    oriented_point_annotation_files_to_metadata_files: Dict[str, str],
    filesystem: FileSystemApi,
) -> Dict[str, List[Dict]]:
    """Load oriented point annotations."""
    return get_ndjson_annotations(oriented_point_annotation_files_to_metadata_files, filesystem)


@pytest.fixture(scope="session")
def instance_seg_annotations(
    instance_seg_annotation_files_to_metadata_files: Dict[str, str],
    filesystem: FileSystemApi,
) -> Dict[str, List[Dict]]:
    """Load instance segmentation annotations."""
    return get_ndjson_annotations(instance_seg_annotation_files_to_metadata_files, filesystem)


@pytest.fixture(scope="session")
def seg_mask_annotation_mrc_headers(
    seg_mask_annotation_mrc_files_to_metadata_files: Dict[str, str],
    filesystem: FileSystemApi,
) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for an mrc annotation file."""
    headers = {}
    for mrc_filename, _ in seg_mask_annotation_mrc_files_to_metadata_files.items():
        headers[mrc_filename] = get_header(mrc_filename, filesystem)

    return headers


@pytest.fixture(scope="session")
def seg_mask_annotation_zarr_headers(
    seg_mask_annotation_zarr_files_to_metadata_files: Dict[str, str],
    filesystem: FileSystemApi,
) -> Dict[str, Dict]:
    """Get the zattrs and zarray data for a zarr annotation file. Dictionary structure: headers = {annotation_a_filename: {zattrs": Dict, "zarrays": Dict}}, annotation_b_filename: ...}."""
    headers = {}
    for zarr_filename, _ in seg_mask_annotation_zarr_files_to_metadata_files.items():
        headers[zarr_filename] = {
            "zattrs": get_zattrs(zarr_filename, filesystem),
            "zarrays": get_zarrays(zarr_filename, filesystem),
        }

    return headers
