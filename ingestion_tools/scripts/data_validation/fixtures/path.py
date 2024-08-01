"""
Fixtures for files and directories on the s3 bucket.
Paths returned as strings (singular fixture name) or lists of strings (plural fixture name).
"""

import os
from typing import Any, Dict, List

import pytest

from common.fs import FileSystemApi


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


@pytest.fixture(scope="session")
def frames_dir(run_dir: str, tiltseries_metadata: Dict[str, Any], filesystem: FileSystemApi) -> str:
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
def tiltseries_mrc_files(
    tiltseries_dir: str,
    tiltseries_metadata: Dict[str, Any],
    filesystem: FileSystemApi,
) -> List[str]:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].mrc"""
    files = [f"{tiltseries_dir}/{tsmrc}" for tsmrc in tiltseries_metadata["mrc_files"]]
    for file in files:
        if not filesystem.s3fs.exists(file):
            pytest.fail(f"Tilt series mrc file not found: {file}")
    return files


@pytest.fixture(scope="session")
def tiltseries_zarr_files(
    tiltseries_dir: str,
    tiltseries_metadata: Dict[str, Any],
    filesystem: FileSystemApi,
) -> List[str]:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].zarr"""
    files = [f"{tiltseries_dir}/{tiltseries_metadata['omezarr_dir']}"]
    for file in files:
        if not filesystem.s3fs.exists(file):
            pytest.fail(f"Tilt series OME-Zarr file not found: {file}")
    return files


@pytest.fixture(scope="session")
def tiltseries_basenames(
    tiltseries_zarr_files: List[str],
) -> List[str]:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name]"""
    basenames = [os.path.splitext(zarr)[0] for zarr in tiltseries_zarr_files]
    return basenames


@pytest.fixture(scope="session")
def tiltseries_mdoc_file(tiltseries_basenames: List[str], filesystem: FileSystemApi) -> List[str]:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].mdoc"""
    files = [f"{tsbn}.mdoc" for tsbn in tiltseries_basenames if filesystem.s3fs.exists(f"{tsbn}.mdoc")]
    if len(files) == 0:
        pytest.skip("No mdoc files found.")
    return files


@pytest.fixture(scope="session")
def tiltseries_rawtlt_file(tiltseries_basenames: List[str], filesystem: FileSystemApi) -> List[str]:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].rawtlt"""
    files = [f"{tsbn}.rawtlt" for tsbn in tiltseries_basenames if filesystem.s3fs.exists(f"{tsbn}.rawtlt")]
    if len(files) == 0:
        pytest.skip("No rawtlt files found.")
    return files


@pytest.fixture(scope="session")
def tiltseries_tlt_file(tiltseries_basenames: List[str], filesystem: FileSystemApi) -> List[str]:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_name].tlt"""
    files = [f"{tsbn}.tlt" for tsbn in tiltseries_basenames if filesystem.s3fs.exists(f"{tsbn}.tlt")]
    if len(files) == 0:
        pytest.skip("No tlt files found.")
    return files


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
def canonical_tomo_mrc_files(
    canonical_tomo_dir: str,
    canonical_tomogram_metadata: Dict[str, Any],
    filesystem: FileSystemApi,
) -> List[str]:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/CanonicalTomogram/[tomo_name].mrc"""
    files = [f"{canonical_tomo_dir}/{ctmrc}" for ctmrc in canonical_tomogram_metadata["mrc_files"]]
    for file in files:
        if not filesystem.s3fs.exists(file):
            pytest.fail(f"Canonical tomogram mrc file not found: {file}")
    return files


@pytest.fixture(scope="session")
def canonical_tomo_zarr_files(
    canonical_tomo_dir: str,
    canonical_tomogram_metadata: Dict[str, Any],
    filesystem: FileSystemApi,
) -> List[str]:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/CanonicalTomogram/[tomo_name].zarr"""
    files = [f"{canonical_tomo_dir}/{canonical_tomogram_metadata['omezarr_dir']}"]
    for file in files:
        if not filesystem.s3fs.exists(file):
            pytest.fail(f"Canonical tomogram OME-Zarr file not found: {file}")
    return files


@pytest.fixture(scope="session")
def canonical_tomo_basenames(
    canonical_tomo_zarr_files: List[str],
) -> List[str]:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/CanonicalTomogram/[tomo_name]"""
    basenames = [os.path.splitext(zarr)[0] for zarr in canonical_tomo_zarr_files]
    return basenames


@pytest.fixture(scope="session")
def annotations_dir(voxel_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/Annotations"""
    dst = f"{voxel_dir}/Annotations"
    if filesystem.s3fs.exists(dst):
        return dst
    else:
        pytest.skip(f"Annotations directory not found: {dst}")


@pytest.fixture(scope="session")
def annotation_meta_files(annotations_dir: str, filesystem: FileSystemApi) -> List[str]:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/Annotations/[annotation_name].json"""
    files = filesystem.glob(f"{annotations_dir}/*.json")

    if len(files) == 0:
        pytest.skip("No annotation metadata files found.")

    return files


@pytest.fixture(scope="session")
def point_annotation_files(
    bucket: str,
    annotation_metadata: Dict[str, Any],
    filesystem: FileSystemApi,
) -> Dict[str, List[str]]:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/Annotations/[annotation_name].ndjson"""

    point_files = {}
    count = 0

    for filename, metadata in annotation_metadata.items():
        point_files[filename] = []
        for annot in metadata["files"]:
            if annot["shape"] == "Point":
                ndfile = f"s3://{bucket}/{annot['path']}"
                if not filesystem.s3fs.exists(ndfile):
                    pytest.fail(f"Point annotation file not found: {ndfile}")

                point_files[filename].append(ndfile)
                count += 1

    if count == 0:
        pytest.skip("No point annotation files found.")

    return point_files


@pytest.fixture(scope="session")
def oriented_point_annotation_files(
    bucket: str,
    annotation_metadata: Dict[str, Any],
    filesystem: FileSystemApi,
) -> Dict[str, List[str]]:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/Annotations/[annotation_name].ndjson"""

    point_files = {}
    count = 0

    for filename, metadata in annotation_metadata.items():
        point_files[filename] = []
        for annot in metadata["files"]:
            if annot["shape"] == "OrientedPoint":
                ndfile = f"s3://{bucket}/{annot['path']}"
                if not filesystem.s3fs.exists(ndfile):
                    pytest.fail(f"OrientedPoint annotation file not found: {ndfile}")

                point_files[filename].append(ndfile)
                count += 1

    if count == 0:
        pytest.skip("No oriented point annotation files found.")

    return point_files


@pytest.fixture(scope="session")
def seg_mask_annotation_mrc_files(
    bucket: str,
    annotation_metadata: Dict[str, Any],
    filesystem: FileSystemApi,
) -> Dict[str, List[str]]:
    """[Dataset]/[ExperimentRun]/Tomograms/VoxelSpacing[voxel_spacing]/Annotations/[annotation_name].mrc"""

    mrc_files = {}
    count = 0

    for filename, metadata in annotation_metadata.items():
        mrc_files[filename] = []
        for annot in metadata["files"]:
            if annot["shape"] == "SegmentationMask" and annot["format"] == "mrc":
                mrcfile = f"s3://{bucket}/{annot['path']}"
                if not filesystem.s3fs.exists(mrcfile):
                    pytest.fail(f"OrientedPoint annotation file not found: {mrcfile}")

                mrc_files[filename].append(mrcfile)
                count += 1

    if count == 0:
        pytest.skip("No segmask mrc annotation files found.")

    return mrc_files
