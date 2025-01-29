"""
Any fixtures involving loading data from the bucket.
"""

import json
import os
from typing import Dict, List, Union

import data_validation.shared.util as helper_util
import mdocfile
import ndjson
import pandas as pd
import pytest
import tifffile
from mrcfile.mrcinterpreter import MrcInterpreter

from common.fs import FileSystemApi

# ==================================================================================================
# Dataset fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def dataset_metadata(dataset_metadata_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the dataset metadata."""
    with filesystem.open(dataset_metadata_file, "r") as f:
        return json.load(f)


# ==================================================================================================
# Run fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def run_metadata(run_meta_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the run metadata."""
    with filesystem.open(run_meta_file, "r") as f:
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
    return helper_util.get_tiff_mrc_headers(frames_files, filesystem)


# ==================================================================================================
# Gain fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def gain_headers(
    gain_files: List[str],
    filesystem: FileSystemApi,
) -> Dict[str, Union[List[tifffile.TiffPage], MrcInterpreter]]:
    """Get the mrc file headers for a gain file."""
    return helper_util.get_tiff_mrc_headers(gain_files, filesystem)


# ==================================================================================================
# Tiltseries & RawTilt fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def tiltseries_mrc_header(tiltseries_mrc_file: str, filesystem: FileSystemApi) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for a tilt series."""
    return {tiltseries_mrc_file: helper_util.get_mrc_header(tiltseries_mrc_file, filesystem)}


@pytest.fixture(scope="session")
def tiltseries_zarr_metadata(tiltseries_zarr_file: str, filesystem: FileSystemApi) -> Dict[str, Dict[str, Dict]]:
    """Get the zattrs and zarray data for a zarr tilt series.
    Dictionary structure: metadata = {tiltseries_a_filename: {"zattrs": Dict, "zarrays": Dict}"""
    return {tiltseries_zarr_file: helper_util.get_zarr_metadata(tiltseries_zarr_file, filesystem)}


@pytest.fixture(scope="session")
def tiltseries_metadata(tiltseries_meta_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the tiltseries metadata."""
    with filesystem.open(tiltseries_meta_file, "r") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def raw_tilt_data(raw_tilt_file: str, filesystem: FileSystemApi) -> pd.DataFrame:
    """Load the tiltseries raw tilt."""
    with filesystem.open(raw_tilt_file, "r") as f:
        return pd.read_csv(f, sep=r"\s+", header=None, names=["TiltAngle"])


# ==================================================================================================
# Frames fixtures
# ==================================================================================================
@pytest.fixture(scope="session")
def mdoc_data(mdoc_file: str, filesystem: FileSystemApi) -> pd.DataFrame:
    """Load the tiltseries mdoc files and return a concatenated DataFrame."""
    return mdocfile.read(filesystem.localreadable(mdoc_file))


# ==================================================================================================
# Alignment & Tilt fixtures
# ==================================================================================================
@pytest.fixture(scope="session")
def alignment_metadata(alignment_metadata_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the alignment metadata."""
    with filesystem.open(alignment_metadata_file, "r") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def alignment_tiltseries_metadata(alignment_tiltseries_metadata_file: Dict, filesystem: FileSystemApi) -> Dict:
    """Load the tiltseries metadata for this alignment"""
    with filesystem.open(alignment_tiltseries_metadata_file, "r") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def alignment_tilt(alignment_tilt_file: str, filesystem: FileSystemApi) -> pd.DataFrame:
    """Load the alignment tilt."""
    with filesystem.open(alignment_tilt_file, "r") as f:
        return pd.read_csv(f, sep=r"\s+", header=None, names=["TiltAngle"])

@pytest.fixture(scope="session")
def alignment_tiltseries_raw_tilt(alignment_tiltseries_rawtilt_file: str, filesystem: FileSystemApi) -> pd.DataFrame:
    """Load the tiltseries raw tilt for this alignment."""
    with filesystem.open(alignment_tiltseries_rawtilt_file, "r") as f:
        return pd.read_csv(f, sep=r"\s+", header=None, names=["TiltAngle"])


# ==================================================================================================
# Tomogram fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def tomo_mrc_header(tomo_mrc_file: str, filesystem: FileSystemApi) -> Dict[str, MrcInterpreter]:
    """Get the mrc file headers for a tomogram."""
    return {tomo_mrc_file: helper_util.get_mrc_header(tomo_mrc_file, filesystem)}


@pytest.fixture(scope="session")
def tomo_zarr_header(tomo_zarr_file: str, filesystem: FileSystemApi) -> Dict[str, Dict[str, Dict]]:
    """
    Get the zattrs and zarray data for a tomogram.
    Dictionary structure: headers = {tomo_a_filename: {"zattrs": Dict, "zarrays": Dict}}.
    """
    return {tomo_zarr_file: helper_util.get_zarr_metadata(tomo_zarr_file, filesystem)}


@pytest.fixture(scope="session")
def tomogram_metadata(tomo_meta_file: str, filesystem: FileSystemApi) -> Dict:
    """Load the tomogram metadata."""
    with filesystem.open(tomo_meta_file, "r") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def all_vs_tomogram_metadata(voxel_dir: str, filesystem: FileSystemApi) -> list[Dict]:
    """Load all tomogram metadata for this voxel spacing."""
    metadatas = []
    for item in filesystem.glob(os.path.join(voxel_dir, "Tomograms/*/tomogram_metadata.json")):
        with filesystem.open(item, "r") as f:
            metadatas.append(json.load(f))
    return metadatas


# ==================================================================================================
# Neuroglancer fixtures
# ==================================================================================================


@pytest.fixture(scope="session")
def neuroglancer_configs(neuroglancer_config_files: List[str], filesystem: FileSystemApi) -> Dict:
    """Load the neuroglancer config."""
    configs = []
    for file in neuroglancer_config_files:
        with filesystem.open(file, "r") as f:
            configs.append(json.load(f))
    return configs


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

def load_metadata_dict(files_dict: Dict[str, str], filesystem: FileSystemApi) -> Dict[str, Dict]:
    """Load the annotation metadata, keyed by path."""
    metadata_objs = {}
    for anno_fname, file in files_dict.items():
        with filesystem.open(file, "r") as f:
            metadata_objs[anno_fname] = json.load(f)

    return metadata_objs

@pytest.fixture(scope="session")
def point_annotation_files_to_metadata(point_annotation_files_to_metadata_files: Dict[str, str], filesystem: FileSystemApi) -> Dict:
    """Load the annotation metadata, keyed by path."""
    return load_metadata_dict(point_annotation_files_to_metadata_files, filesystem)

@pytest.fixture(scope="session")
def oriented_point_annotation_files_to_metadata(oriented_point_annotation_files_to_metadata_files: Dict[str, str], filesystem: FileSystemApi) -> Dict:
    """Load the annotation metadata, keyed by path."""
    return load_metadata_dict(oriented_point_annotation_files_to_metadata_files, filesystem)

@pytest.fixture(scope="session")
def instance_seg_annotation_files_to_metadata(instance_seg_annotation_files_to_metadata_files: Dict[str, str], filesystem: FileSystemApi) -> Dict:
    """Load the annotation metadata, keyed by path."""
    return load_metadata_dict(instance_seg_annotation_files_to_metadata_files, filesystem)

@pytest.fixture(scope="session")
def seg_mask_annotation_files_to_metadata(seg_mask_annotation_mrc_files_to_metadata_files: Dict[str, str], filesystem: FileSystemApi) -> Dict:
    """Load the annotation metadata, keyed by path."""
    return load_metadata_dict(seg_mask_annotation_mrc_files_to_metadata_files, filesystem)


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
        headers[mrc_filename] = helper_util.get_mrc_header(mrc_filename, filesystem)

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
        headers[zarr_filename] = helper_util.get_zarr_metadata(zarr_filename, filesystem)

    return headers
