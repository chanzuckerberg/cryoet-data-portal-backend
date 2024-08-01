"""
Any fixtures involving loading data from the bucket.
"""

import json
from typing import Dict, List

import mdocfile
import ndjson
import pandas as pd
import pytest
from data_validation_common.mrc import get_header
from mrcfile.mrcinterpreter import MrcInterpreter

from common.fs import FileSystemApi


### Tilt series fixtures ###
@pytest.fixture(scope="session")
def tiltseries_mrc_headers(tiltseries_mrc_files: List[str]) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for a tilt series."""
    headers = {}
    for file in tiltseries_mrc_files:
        try:
            headers[file] = get_header(file)
        except Exception as _:
            pytest.fail(f"Failed to get header for {file}")

    return headers


@pytest.fixture(scope="session")
def tiltseries_metadata(tiltseries_meta_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the tiltseries metadata."""
    with filesystem.open(tiltseries_meta_file, "r") as f:
        return json.load(f)


@pytest.fixture()
def tiltseries_mdoc(tiltseries_mdoc_file: str, filesystem: FileSystemApi) -> pd.DataFrame:
    """Load the tiltseries mdoc."""

    with filesystem.open(tiltseries_mdoc_file, "r") as f:
        return mdocfile.read(f)


@pytest.fixture()
def tiltseries_tlt(tiltseries_tlt_file: str, filesystem: FileSystemApi) -> pd.DataFrame:
    """Load the tiltseries tlt."""

    with filesystem.open(tiltseries_tlt_file, "r") as f:
        return pd.read_csv(f, sep=r"\s+", header=None, names=["tilt_angle"])


### Tomogram fixtures ###
@pytest.fixture(scope="session")
def canonical_tomo_mrc_headers(canonical_tomo_mrc_files: List[str]) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for a tomogram."""
    headers = {}
    for file in canonical_tomo_mrc_files:
        try:
            headers[file] = get_header(file)
        except Exception as _:
            pytest.fail(f"Failed to get header for {file}")

    return headers


@pytest.fixture(scope="session")
def canonical_tomogram_metadata(canonical_tomo_meta_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the canonical tomogram metadata."""
    with filesystem.open(canonical_tomo_meta_file, "r") as f:
        return json.load(f)


### Annotation fixtures ###
@pytest.fixture(scope="session")
def annotation_metadata(annotation_meta_files: str, filesystem: FileSystemApi) -> Dict[str, Dict]:
    """Load the annotation metadata."""
    metadata_objs = {}

    for file in annotation_meta_files:
        with filesystem.open(file, "r") as f:
            metadata_objs[file] = json.load(f)

    return metadata_objs


@pytest.fixture(scope="session")
def point_annotations(
    point_annotation_files: Dict[str, List[str]],
    filesystem: FileSystemApi,
) -> Dict[str, Dict[str, Dict]]:
    """Load point annotations."""
    annotations = {}
    for annoname, files in point_annotation_files.items():
        annotations[annoname] = {}
        for file in files:
            with filesystem.open(file, "r") as f:
                annotations[annoname][file] = ndjson.load(f)

    return annotations


@pytest.fixture(scope="session")
def oriented_point_annotations(
    oriented_point_annotation_files: Dict[str, List[str]],
    filesystem: FileSystemApi,
) -> Dict[str, Dict[str, Dict]]:
    """Load oriented point annotations."""
    annotations = {}
    for annoname, files in oriented_point_annotation_files.items():
        annotations[annoname] = {}
        for file in files:
            with filesystem.open(file, "r") as f:
                annotations[annoname][file] = ndjson.load(f)

    return annotations


@pytest.fixture(scope="session")
def seg_mask_annotation_mrc_headers(
    seg_mask_annotation_mrc_files: Dict[str, List[str]],
) -> Dict[str, Dict[str, MrcInterpreter]]:
    """Get the mrc file headers for an mrc annotation file."""
    annotations = {}
    for annoname, files in seg_mask_annotation_mrc_files.items():
        annotations[annoname] = {}
        for file in files:
            try:
                annotations[annoname][file] = get_header(file)
            except Exception as _:
                pytest.fail(f"Failed to get header for {file}")

    return annotations
