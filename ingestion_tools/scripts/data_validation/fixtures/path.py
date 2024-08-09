"""
Fixtures for files and directories on the s3 bucket.
Paths returned as strings (singular fixture name) or lists of strings (plural fixture name).
Note that some of these fixtures, although session-scoped, can be re-initialized for every parameterized
run_name and voxel_spacing combination.
"""

import os
from typing import Dict, List, Optional

import pytest

from common.fs import FileSystemApi

# =============================================================================
# FS & Dataset fixtures
# =============================================================================


@pytest.fixture(scope="session")
def filesystem() -> FileSystemApi:
    return FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)


@pytest.fixture(scope="session")
def dataset_dir(bucket: str, dataset: str) -> str:
    """[Dataset]"""
    return f"s3://{bucket}/{dataset}"


@pytest.fixture(scope="session")
def dataset_meta_file(dataset_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/dataset_metadata.json"""
    dst = f"{dataset_dir}/dataset_metadata.json"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.fail(f"Dataset metadata file not found: {dst}")


# =============================================================================
# Run fixtures
# =============================================================================


@pytest.fixture(scope="session")
def run_dir(dataset_dir: str, run_name: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]"""
    dst = f"{dataset_dir}/{run_name}"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.fail(f"Run directory {dst} does not exist.")


@pytest.fixture(scope="session")
def run_meta_file(run_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/run_metadata.json"""
    dst = f"{run_dir}/run_metadata.json"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.fail(f"Run metadata file not found: {dst}")


# =============================================================================
# Run-specific fixtures, Frames
# =============================================================================


@pytest.fixture(scope="session")
def frames_dir(run_dir: str, tiltseries_metadata: Dict, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Frames"""
    dst = f"{run_dir}/Frames"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        if tiltseries_metadata["frames_count"] > 0:
            pytest.fail(f"Frames directory not present: {dst}")
        else:
            pytest.skip(f"Frames directory not present: {dst}")


@pytest.fixture(scope="session")
def frame_acquisition_order_file(frames_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Frames/frame_acquisition_order.json"""
    dst = f"{frames_dir}/frame_acquisition_order.json"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.fail(f"Frame acquisition order file not found: {dst}")


# =============================================================================
# Run-specific fixtures, Tiltseries & RawTilt
# =============================================================================


@pytest.fixture(scope="session")
def tiltseries_dir(run_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries"""
    dst = f"{run_dir}/TiltSeries"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.skip(f"TiltSeries directory not found: {dst}")


@pytest.fixture(scope="session")
def tiltseries_meta_file(
    tiltseries_dir: str,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/tiltseries_metadata.json"""
    dst = f"{tiltseries_dir}/tiltseries_metadata.json"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.fail(f"Tilt series metadata file not found: {dst}")


@pytest.fixture(scope="session")
def tiltseries_mrc_file(
    tiltseries_dir: str,
    tiltseries_metadata: Dict,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].mrc"""
    # TODO FIXME List[str] mrc_files should really just become str mrc_file, and then adjust this fixture accordingly
    file = tiltseries_dir + "/" + tiltseries_metadata["mrc_files"][0]
    if not filesystem.s3fs.exists(file):
        pytest.fail(f"Tilt series mrc file not found: {file}")
    return file


@pytest.fixture(scope="session")
def tiltseries_zarr_file(
    tiltseries_dir: str,
    tiltseries_metadata: Dict,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].zarr"""
    file = f"{tiltseries_dir}/{tiltseries_metadata['omezarr_dir']}"
    if not filesystem.s3fs.exists(file):
        pytest.fail(f"Tilt series OME-Zarr file not found: {file}")


@pytest.fixture(scope="session")
def tiltseries_basename(
    tiltseries_zarr_file: str,
) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name]"""
    return os.path.splitext(tiltseries_zarr_file)[0]


@pytest.fixture(scope="session")
def tiltseries_mdoc_file(tiltseries_basename: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].mdoc"""
    if filesystem.s3fs.exists(f"{tiltseries_basename}.mdoc"):
        return f"{tiltseries_basename}.mdoc"
    else:
        pytest.skip("No mdoc file found.")


@pytest.fixture(scope="session")
def tiltseries_rawtlt_file(tiltseries_basename: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].rawtlt"""
    if filesystem.s3fs.exists(f"{tiltseries_basename}.rawtlt"):
        return f"{tiltseries_basename}.rawtlt"
    else:
        pytest.skip("No rawtlt file found.")


@pytest.fixture(scope="session")
def tiltseries_tlt_file(tiltseries_basename: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].tlt"""
    if filesystem.s3fs.exists(f"{tiltseries_basename}.tlt"):
        return f"{tiltseries_basename}.tlt"
    else:
        pytest.skip("No tlt file found.")


# =============================================================================
# Run and voxel-specific fixtures, Tomograms
# =============================================================================


@pytest.fixture(scope="session")
def tomograms_dir(run_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Tomograms"""
    dst = f"{run_dir}/Tomograms"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.fail(f"Tomograms directory not found: {dst}")


@pytest.fixture(scope="session")
def voxel_dir(
    tomograms_dir: str,
    voxel_spacing: float,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]"""

    dst = f"{tomograms_dir}/VoxelSpacing{voxel_spacing:.3f}"

    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.fail(f"VoxelSpacing directory not found: {dst}")


@pytest.fixture(scope="session")
def canonical_tomo_dir(voxel_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/CanonicalTomogram"""
    dst = f"{voxel_dir}/CanonicalTomogram"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.fail(f"CanonicalTomogram directory not found: {dst}")


@pytest.fixture(scope="session")
def canonical_tomo_meta_file(
    canonical_tomo_dir: str,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/CanonicalTomogram/tomogram_metadata.json"""
    dst = f"{canonical_tomo_dir}/tomogram_metadata.json"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.fail(f"Canonical tomogram metadata file not found: {dst}")


@pytest.fixture(scope="session")
def canonical_tomo_mrc_file(
    canonical_tomo_dir: str,
    canonical_tomogram_metadata: Dict,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/CanonicalTomogram/[tomo_name].mrc"""
    # TODO FIXME List[str] mrc_files should really just become str mrc_file, and then adjust this fixture accordingly
    file = canonical_tomo_dir + "/" + canonical_tomogram_metadata["mrc_files"][0]
    if not filesystem.s3fs.exists(file):
        pytest.fail(f"Canonical tomogram mrc file not found: {file}")
    return file


@pytest.fixture(scope="session")
def canonical_tomo_zarr_file(
    canonical_tomo_dir: str,
    canonical_tomogram_metadata: Dict,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/CanonicalTomogram/[tomo_name].zarr"""
    file = f"{canonical_tomo_dir}/{canonical_tomogram_metadata['omezarr_dir']}"
    if not filesystem.s3fs.exists(file):
        pytest.fail(f"Canonical tomogram OME-Zarr file not found: {file}")
    return file


@pytest.fixture(scope="session")
def canonical_tomo_basename(
    canonical_tomo_zarr_file: str,
) -> str:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/CanonicalTomogram/[tomo_name]"""
    return os.path.splitext(canonical_tomo_zarr_file)[0]


# =============================================================================
# Run and voxel-specific fixtures, Annotations
# =============================================================================


@pytest.fixture(scope="session")
def annotations_dir(voxel_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/Annotations"""
    dst = f"{voxel_dir}/Annotations"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.skip(f"Annotations directory not found: {dst}")


@pytest.fixture(scope="session")
def annotation_metadata_files(annotations_dir: str, filesystem: FileSystemApi) -> List[str]:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/Annotations/[annotation_name].json"""
    files = filesystem.glob(f"{annotations_dir}/*.json")

    if len(files) == 0:
        pytest.skip("No annotation metadata files found.")

    return files


def get_annotation_files(
    bucket: str,
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
    name: str,
    format: Optional[str] = None,
) -> Dict[str, str]:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/Annotations/[annotation_name].*
    Returns a dictionary of annotation files, annotation_filename -> metadata_filename.
    """

    annotation_files = {}
    count = 0

    for metadata_filename, metadata in annotation_metadata.items():
        for annotation in metadata["files"]:
            if annotation["shape"] == name and (format is None or annotation["format"] == format):
                file = f"s3://{bucket}/{annotation['path']}"
                if not filesystem.s3fs.exists(file):
                    pytest.fail(f"{name} {format if format else ''} annotation file not found: {file}")

                annotation_files[file] = metadata_filename
                count += 1

    if count == 0:
        pytest.skip(f"No {name} {format if format else ''} annotation files found.")

    return annotation_files


@pytest.fixture(scope="session")
def point_annotation_files_to_metadata_files(
    bucket: str,
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files(bucket, annotation_metadata, filesystem, "Point")


@pytest.fixture(scope="session")
def oriented_point_annotation_files_to_metadata_files(
    bucket: str,
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files(bucket, annotation_metadata, filesystem, "OrientedPoint")


@pytest.fixture(scope="session")
def instance_seg_annotation_files_to_metadata_files(
    bucket: str,
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files(bucket, annotation_metadata, filesystem, "InstanceSegmentation")


@pytest.fixture(scope="session")
def seg_mask_annotation_mrc_files_to_metadata_files(
    bucket: str,
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files(bucket, annotation_metadata, filesystem, "SegmentationMask", "mrc")


@pytest.fixture(scope="session")
def seg_mask_annotation_zarr_files_to_metadata_files(
    bucket: str,
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files(bucket, annotation_metadata, filesystem, "SegmentationMask", "zarr")
