"""
Fixtures for files and directories on the s3 bucket.
Paths returned as strings (singular fixture name) or lists of strings (plural fixture name).
Note that some of these fixtures, although session-scoped, can be re-initialized for every parametrized
run_name and voxel_spacing combination.
"""

import os
from typing import Dict, List, Optional

import pytest

from common.fs import FileSystemApi


@pytest.fixture(scope="session")
def filesystem() -> FileSystemApi:
    return FileSystemApi.get_fs_api(mode="s3", force_overwrite=False)


# =============================================================================
# Dataset fixtures
# =============================================================================


@pytest.fixture(scope="session")
def dataset_dir(bucket: str, dataset: str) -> str:
    """[Dataset]"""
    return f"s3://{bucket}/{dataset}"


@pytest.fixture(scope="session")
def dataset_metadata_file(dataset_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/dataset_metadata.json"""
    dst = f"{dataset_dir}/dataset_metadata.json"
    if filesystem.exists(dst):
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
    if filesystem.exists(dst):
        return dst
    else:
        pytest.fail(f"Run directory {dst} does not exist.")


@pytest.fixture(scope="session")
def run_meta_file(run_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/run_metadata.json"""
    dst = f"{run_dir}/run_metadata.json"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.fail(f"Run metadata file not found: {dst}")


# =============================================================================
# Run-specific fixtures, Frames
# =============================================================================


@pytest.fixture(scope="session")
def frames_dir(run_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Frames"""
    dst = f"{run_dir}/Frames"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.skip(f"Frames directory not present: {dst}")


@pytest.fixture(scope="session")
def frames_files(frames_dir: str, filesystem: FileSystemApi) -> List[str]:
    """[Dataset]/[ExperimentRun]/Frames/*"""
    files = filesystem.glob(f"{frames_dir}/*")
    # Exclude mdoc files, add s3 prefix
    refined_files = ["s3://" + file for file in files if ".mdoc" not in file]
    # mdoc files are in the folder, but just no frames
    if len(refined_files) == 0 and len(files) != 0:
        pytest.skip(f"No frame files in frames directory: {frames_dir}")

    return refined_files


# =============================================================================
# Run-specific fixtures, Gain
# =============================================================================


@pytest.fixture(scope="session")
def gain_dir(run_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Frames"""
    dst = f"{run_dir}/Gains"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.skip(f"Gain directory not found: {dst}")


@pytest.fixture(scope="session")
def gain_files(run_name: str, gain_dir: str, filesystem: FileSystemApi) -> List[str]:
    """[Dataset]/[ExperimentRun]/Frames/[run_name]*_gain*"""
    files = filesystem.glob(f"{gain_dir}/*")
    if len(files) == 0:
        pytest.skip("No gain files found.")

    for file in files:
        assert not file.endswith(".dm4"), f"Invalid gain file extension: {file} (should be .mrc)"

    return files


# =============================================================================
# Run-specific fixtures, Tiltseries & RawTilt
# =============================================================================


@pytest.fixture(scope="session")
def tiltseries_dir(run_dir: str, ts_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries"""
    dst = f"{run_dir}/TiltSeries/{ts_dir}"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.skip(f"TiltSeries directory not found: {dst}")

@pytest.fixture(scope="session")
def alignment_dir(run_dir: str, aln_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Alignments/[aln_dir]"""
    dst = f"{run_dir}/Alignments/{aln_dir}"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.skip(f"Alignment directory not found: {dst}")

@pytest.fixture(scope="session")
def alignment_tiltseries_metadata_file(alignment_metadata: Dict, bucket: str) -> str:
    """Load the tiltseries metadata for this alignment"""
    if "tiltseries_path" not in alignment_metadata:
        pytest.skip("No tiltseries path in alignment metadata")
    return f"{bucket}/{alignment_metadata['tiltseries_path']}"

@pytest.fixture(scope="session")
def alignment_tiltseries_rawtilt_file(alignment_tiltseries_metadata_file: Dict, filesystem: FileSystemApi) -> str:
    """Load the tiltseries metadata for this alignment"""
    ts_dir = os.path.dirname(alignment_tiltseries_metadata_file)
    files = filesystem.glob(f"{ts_dir}/*.rawtlt")
    if len(files) == 0:
        pytest.skip("No rawtlt files found.")
    return files[0]


@pytest.fixture(scope="session")
def tiltseries_meta_file(
    tiltseries_dir: str,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_dir]/tiltseries_metadata.json"""
    dst = f"{tiltseries_dir}/tiltseries_metadata.json"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.fail(f"Tilt series metadata file not found: {dst}")


@pytest.fixture(scope="session")
def tiltseries_mrc_file(
    tiltseries_dir: str,
    bucket: str,
    tiltseries_metadata: Dict,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_dir]/[ts_name].mrc"""

    file = os.path.join(bucket, tiltseries_metadata['mrc_file'])
    if not filesystem.exists(file):
        pytest.fail(f"Tilt series mrc file not found: {file}")
    return file


@pytest.fixture(scope="session")
def tiltseries_zarr_file(
    tiltseries_dir: str,
    bucket: str,
    tiltseries_metadata: Dict,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_dir]/[ts_name].zarr"""
    file = os.path.join(bucket, tiltseries_metadata['omezarr_dir'])
    if not filesystem.exists(file):
        pytest.fail(f"Tilt series Zarr file not found: {file}")
    return file


@pytest.fixture(scope="session")
def tiltseries_basename(
    tiltseries_zarr_file: str,
) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_dir]/[ts_name]"""
    return os.path.splitext(tiltseries_zarr_file)[0]


@pytest.fixture(scope="session")
def mdoc_file(frames_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Frames/*.mdoc"""
    mdoc_files = filesystem.glob(f"{frames_dir}/*.mdoc")
    if len(mdoc_files) == 1:
        return mdoc_files[0]
    elif len(mdoc_files) > 1:
        pytest.fail(f"Multiple mdoc files found: {mdoc_files}")
    else:
        pytest.skip("No mdoc file found.")


@pytest.fixture(scope="session")
def alignment_metadata_file(alignment_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Alignments/[alignment_dir]/[run_name].tlt"""
    metadata_file = filesystem.glob(f"{alignment_dir}/alignment_metadata.json")
    if len(metadata_file) == 0:
        pytest.skip("No alignment metadata file found.")
    return metadata_file[0]

@pytest.fixture(scope="session")
def alignment_tilt_file(alignment_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Alignments/[alignment_dir]/[run_name].tlt"""
    tlt_files = filesystem.glob(f"{alignment_dir}/*.tlt")
    if len(tlt_files) == 0:
        pytest.skip("No tlt file found.")
    return tlt_files[0]


@pytest.fixture(scope="session")
def tiltseries_rawtilt_file(tiltseries_basename: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/TiltSeries/[ts_dir]/[ts_name].rawtlt"""
    rawtlt_files = filesystem.glob(f"{tiltseries_basename}.rawtlt")
    if len(rawtlt_files) == 0:
        pytest.skip("No rawtlt file found.")
    return rawtlt_files[0]


# =============================================================================
# Run and voxel-specific fixtures, Tomograms
# =============================================================================


@pytest.fixture(scope="session")
def tomograms_dir(run_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Reconstructions"""
    dst = f"{run_dir}/Reconstructions"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.fail(f"Tomograms directory not found: {dst}")


@pytest.fixture(scope="session")
def voxel_dir(
    tomograms_dir: str,
    voxel_spacing: str,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]"""

    dst = f"{tomograms_dir}/VoxelSpacing{voxel_spacing}"

    if filesystem.exists(dst):
        return dst
    else:
        pytest.fail(f"VoxelSpacing directory not found: {dst}")


@pytest.fixture(scope="session")
def tomo_dir(voxel_dir: str, tomodir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/[tomodir]"""
    dst = f"{voxel_dir}/Tomograms/{tomodir}"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.fail(f"Tomogram directory not found: {dst}")


@pytest.fixture(scope="session")
def tomo_meta_file(
    tomo_dir: str,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Tomograms/[tomodir]/tomogram_metadata.json"""
    dst = f"{tomo_dir}/tomogram_metadata.json"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.fail(f"Tomogram metadata file not found: {dst}")


@pytest.fixture(scope="session")
def tomo_mrc_file(
    tomo_dir: str,
    bucket: str,
    tomogram_metadata: Dict,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Tomograms/[tomodir]/[tomo_name].mrc"""
    file = os.path.join(bucket, tomogram_metadata['mrc_file'])
    if not filesystem.exists(file):
        pytest.fail(f"Tomogram mrc file not found: {file}")
    return file


@pytest.fixture(scope="session")
def tomo_zarr_file(
    tomo_dir: str,
    bucket: str,
    tomogram_metadata: Dict,
    filesystem: FileSystemApi,
) -> str:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Tomograms/[tomodir]/[tomo_name].zarr"""
    file = os.path.join(bucket, tomogram_metadata['omezarr_dir'])
    if not filesystem.exists(file):
        pytest.fail(f"Tomogram Zarr file not found: {file}")
    return file


# =============================================================================
# Run and voxel-specific fixtures, Neuroglancer
# =============================================================================


@pytest.fixture(scope="session")
def neuroglancer_dir(voxel_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/NeuroglancerPrecompute/"""
    return os.path.join(voxel_dir, "NeuroglancerPrecompute")


@pytest.fixture(scope="session")
def neuroglancer_config_files(
    neuroglancer_dir: str,
    filesystem: FileSystemApi,
) -> List[str]:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/NeuroglancerPrecompute/*neuroglancer_config.json"""
    dst = f"{neuroglancer_dir}/*neuroglancer_config.json"
    return filesystem.glob(dst)


# =============================================================================
# Run and voxel-specific fixtures, Annotations
# =============================================================================


@pytest.fixture(scope="session")
def annotations_dir(voxel_dir: str, filesystem: FileSystemApi) -> str:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Annotations"""
    dst = f"{voxel_dir}/Annotations"
    if filesystem.exists(dst):
        return dst
    else:
        pytest.skip(f"Annotations directory not found: {dst}")


@pytest.fixture(scope="session")
def annotation_files(
    point_annotation_files: List[str],
    oriented_point_annotation_files: List[str],
    instance_seg_annotation_files: List[str],
    seg_mask_annotation_mrc_files: List[str],
) -> List[str]:
    all_files = (
        point_annotation_files
        + oriented_point_annotation_files
        + instance_seg_annotation_files
        + seg_mask_annotation_mrc_files
    )
    assert len(all_files) > 0, "No annotation files found, but folder exists."
    return all_files


@pytest.fixture(scope="session")
def annotation_metadata_files(annotations_dir: str, filesystem: FileSystemApi) -> List[str]:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Annotations/*/[annotation_name].json"""
    return filesystem.glob(f"{annotations_dir}/*/*.json")


def get_annotation_files_to_metadata_files(
    bucket: str,
    annotation_files: List[str],
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
    name: str,
    format: Optional[str] = None,
) -> Dict[str, str]:
    """[Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Annotations/[annotation_name].*
    Helper function for retrieving annotation files and their corresponding metadata files.
    Fails the test if the annotation file is not found for a given metadata file OR if there are any remaining annotation files.
    Returns a dictionary of annotation files, annotation_filename -> metadata_filename.
    """

    remaining_annotation_files = annotation_files.copy()
    corresponding_annotation_files = {}
    count = 0

    for metadata_filename, metadata in annotation_metadata.items():
        for annotation in metadata["files"]:
            if annotation["shape"] == name and (format is None or annotation["format"] == format):
                file = f"s3://{bucket}/{annotation['path']}"
                if not filesystem.exists(file):
                    pytest.fail(f"{name} annotation file not found: {file}")

                corresponding_annotation_files[file] = metadata_filename
                remaining_annotation_files.remove(file)
                count += 1

    if len(remaining_annotation_files) > 0:
        pytest.fail(
            f"Metadata file not found for {len(remaining_annotation_files)} {name} annotation files.",
        )

    if count == 0:
        pytest.skip(f"No {name} annotation files found.")

    return corresponding_annotation_files


@pytest.fixture(scope="session")
def point_annotation_files(annotations_dir: str, filesystem: FileSystemApi) -> List[str]:
    """
    [Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Annotations/*/*_point.ndjson

    Note: for files like this, we don't actually want to skip if there's no files found, because we're testing
    if the metadata and annotation files are consistent. See `get_annotation_files_to_metadata_files` for more info.
    """
    files = filesystem.glob(f"{annotations_dir}/*/*_point.ndjson")
    return ["s3://" + file for file in files]


@pytest.fixture(scope="session")
def point_annotation_files_to_metadata_files(
    bucket: str,
    point_annotation_files: List[str],
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files_to_metadata_files(
        bucket,
        point_annotation_files,
        annotation_metadata,
        filesystem,
        "Point",
    )


@pytest.fixture(scope="session")
def oriented_point_annotation_files(annotations_dir: str, filesystem: FileSystemApi) -> List[str]:
    """
    [Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Annotations/*/*_orientedpoint.ndjson

    Note: for files like this, we don't actually want to skip if there's no files found, because we're testing
    if the metadata and annotation files are consistent. See `get_annotation_files_to_metadata_files` for more info.
    """
    files = filesystem.glob(f"{annotations_dir}/*/*_orientedpoint.ndjson")
    return ["s3://" + file for file in files]


@pytest.fixture(scope="session")
def oriented_point_annotation_files_to_metadata_files(
    bucket: str,
    oriented_point_annotation_files: List[str],
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files_to_metadata_files(
        bucket,
        oriented_point_annotation_files,
        annotation_metadata,
        filesystem,
        "OrientedPoint",
    )


@pytest.fixture(scope="session")
def instance_seg_annotation_files(annotations_dir: str, filesystem: FileSystemApi) -> List[str]:
    """
    [Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Annotations/*/*_instancesegmentation.ndjson

    Note: for files like this, we don't actually want to skip if there's no files found, because we're testing
    if the metadata and annotation files are consistent. See `get_annotation_files_to_metadata_files` for more info.
    """
    files = filesystem.glob(f"{annotations_dir}/*/*_instancesegmentation.ndjson")
    return ["s3://" + file for file in files]


@pytest.fixture(scope="session")
def instance_seg_annotation_files_to_metadata_files(
    bucket: str,
    instance_seg_annotation_files: List[str],
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files_to_metadata_files(
        bucket,
        instance_seg_annotation_files,
        annotation_metadata,
        filesystem,
        "InstanceSegmentation",
    )


@pytest.fixture(scope="session")
def seg_mask_annotation_mrc_files(annotations_dir: str, filesystem: FileSystemApi) -> List[str]:
    """
    [Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Annotations/*/*_segmentationmask.mrc

    Note: for files like this, we don't actually want to skip if there's no files found, because we're testing
    if the metadata and annotation files are consistent. See `get_annotation_files_to_metadata_files` for more info.
    """
    files = filesystem.glob(f"{annotations_dir}/*/*_segmentationmask.mrc")
    return ["s3://" + file for file in files]


@pytest.fixture(scope="session")
def seg_mask_annotation_mrc_files_to_metadata_files(
    bucket: str,
    seg_mask_annotation_mrc_files: List[str],
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files_to_metadata_files(
        bucket,
        seg_mask_annotation_mrc_files,
        annotation_metadata,
        filesystem,
        "SegmentationMask",
        "mrc",
    )


@pytest.fixture(scope="session")
def seg_mask_annotation_zarr_files(annotations_dir: str, filesystem: FileSystemApi) -> List[str]:
    """
    [Dataset]/[ExperimentRun]/Reconstructions/VoxelSpacing[voxel_spacing]/Annotations/*/*_segmentationmask.zarr

    Note: for files like this, we don't actually want to skip if there's no files found, because we're testing
    if the metadata and annotation files are consistent. See `get_annotation_files_to_metadata_files` for more info.
    """
    files = filesystem.glob(f"{annotations_dir}/*/*_segmentationmask.zarr")
    return ["s3://" + file for file in files]


@pytest.fixture(scope="session")
def seg_mask_annotation_zarr_files_to_metadata_files(
    bucket: str,
    annotation_metadata: Dict[str, Dict],
    filesystem: FileSystemApi,
) -> Dict[str, str]:
    return get_annotation_files_to_metadata_files(bucket, annotation_metadata, filesystem, "SegmentationMask", "zarr")
